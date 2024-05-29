import configparser
import requests
import io
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from cls_vk_api import VkApi
from database import Database
from typing import Any


class VKBot:
    config = configparser.ConfigParser()
    config.read("settings.ini")

    def __init__(self):
        self.vk_session = vk_api.VkApi(token=self.config['BOT']['TOKEN'])
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.api = VkApi(self.config['API']['TOKEN'])
        self.db = Database(self.config['DATABASE']['NAME'],
                           self.config['DATABASE']['USER'],
                           self.config['DATABASE']['PASSWORD'],
                           self.config['DATABASE']['HOST'],
                           int(self.config['DATABASE']['PORT']))
        self.current_pair = None

    def send_message(self, user_id, message=None, keyboard=None, attachment=None, template=None):
        self.vk.messages.send(
            user_id=user_id,
            random_id=0,
            keyboard=keyboard,
            message=message,
            attachment=attachment,
            template=template
        )

    def interface(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()
                user_id = event.user_id
                return text, user_id

    @staticmethod
    def start_create_keyboard():
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Избранные', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Настроить фильтры поиска', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
        return keyboard.get_keyboard()

    @staticmethod
    def create_keyboard_gender():
        keyboard = VkKeyboard()
        keyboard.add_button('Парень', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Девушка', color=VkKeyboardColor.POSITIVE)
        return keyboard.get_keyboard()

    @staticmethod
    def create_search_keyboard():
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Дальше', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Добавить в избранные',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Избранные',
                            color=VkKeyboardColor.POSITIVE)
        return keyboard.get_keyboard()

    # @staticmethod
    # def create_add_favorites_inline_keyboard():
    #     keyboard = VkKeyboard(inline=True)
    #     keyboard.add_button("Добавить в избранное", color=VkKeyboardColor.POSITIVE)
    #     return keyboard.get_keyboard()

    def handle_gender_selection(self, selected_gender, user_id, city, age):
        keyboard = self.start_create_keyboard()

        result_user_id = self.db.fetch_one('SELECT user_id FROM users WHERE user_id = %s', (user_id,))

        if result_user_id:
            self.db.execute_query(
                f"UPDATE users SET city = '{city}', sex = '{selected_gender}', age = {age} WHERE user_id = {user_id}")
        else:
            self.db.execute_query('INSERT INTO users (user_id, city, sex, age) VALUES (%s, %s, %s, %s)',
                                  (user_id, city, selected_gender, age))

        self.send_message(user_id, 'Теперь фильтры настроены, далее нажмите кнопку поиск', keyboard)

    def buttons_filter_male_or_female(self, user_id, city, age):
        keyboard = self.create_keyboard_gender()
        self.send_message(user_id, 'Выберите желаемый пол:', keyboard)
        selected_gender, user_id = self.interface()
        self.handle_gender_selection(selected_gender, user_id, city, age)

    def filter_age(self, user_id, city):
        self.send_message(user_id, 'Напишите желаемый возраст:')
        age, user_id = self.interface()
        self.buttons_filter_male_or_female(user_id, city, age)

    def filter_city(self, user_id):
        self.send_message(user_id, 'Напишите название города:')
        city, user_id = self.interface()
        self.filter_age(user_id, city)

    def search(self, city: str, age: int, sex: str,
               user_id: Any, count: int = 3) -> None:
        age_from = age
        age_to = age
        sex_id = 0
        if sex.lower() == "девушка":
            sex_id = 1
        elif sex.lower() == "парень":
            sex_id = 2
        self.api.store_pairs_data(city.capitalize(), sex_id, age_from, age_to, count)
        self.show_pair(user_id)

    def show_pair(self, user_id: int) -> None:
        user = self.api.get_pair_from_storage()
        self.current_pair = user
        msg = f"{user.get("first_last_name")} {user.get("link")}"
        self.send_message(message=msg, user_id=user_id,
                          keyboard=self.create_search_keyboard())
        for photo_link in user.get("photos_links"):
            content = requests.get(photo_link).content
            photo_bytes = io.BytesIO(content)
            upload = vk_api.VkUpload(self.vk)
            photo = upload.photo_messages(photos=[photo_bytes])[0]
            owner_id = photo['owner_id']
            photo_id = photo['id']
            self.send_message(user_id=user_id,
                              attachment=f'photo{owner_id}_{photo_id}')

    def run(self):
        text, user_id = self.interface()

        if text == 'настроить фильтры поиска':
            self.filter_city(user_id)

        elif text == 'поиск':
            # на этом участке предположительно нужно нужно сделать так, чтобы убраит лишнее (лучше через try/except)
            # query = db.fetch_all('SELECT city, sex, age, user_id FROM users WHERE user_id= %s', (user_id,))
            # if query:
            #       for city, sex, age, user_id in query:
            #           self.search(str(city), int(age), str(sex), 3, user_id)
            #   else:
            #           self.send_message(user_id, 'Вы еще не настроили фильтры для поиска')

            result_user_id = self.db.fetch_one(
                'SELECT user_id FROM users WHERE user_id = %s',
                (user_id,))

            if result_user_id:
                query = self.db.fetch_all(
                    'SELECT city, sex, age, user_id FROM users WHERE user_id= %s',
                    (user_id,))
                city, sex, age, user_id = query[0]
                self.search(str(city), int(age), str(sex), user_id)
            else:
                self.send_message(user_id, 'Вы еще не настроили фильтры для поиска')

        elif text == 'дальше':
            if self.api.users_storage:
                self.show_pair(user_id)
            else:
                msg = 'Вы посмотрели все пары, нажмите поиск для генерации новых'
                self.send_message(user_id, msg, keyboard=self.create_search_keyboard())

        elif text == 'старт':
            self.send_message(user_id, 'Добро пожаловать! Я помогу найти для тебя девушку/парня, '
                                       'для начала настрой фильтры поиска', self.start_create_keyboard())

        elif text == 'добавить в избранные':
            first_last_name = self.current_pair.get("first_last_name")
            vk_link = self.current_pair.get("link")
            self.db.add_into_favorites(user_id, first_last_name, vk_link)
            pair_id = self.db.get_pair_id(vk_link)
            for photo_link in self.current_pair.get("photos_links"):
                self.db.add_into_photos(pair_id, photo_link)
            self.send_message(message="Пара успешно добавлена",
                              user_id=user_id,
                              keyboard=self.create_search_keyboard())
        elif text == 'избранные':
            favorites = self.db.create_favorites_data(user_id)
            for user in favorites:
                msg = f"{user.get("first_last_name")} {user.get("link")}"
                self.send_message(message=msg, user_id=user_id)
                for photo_link in user.get("photos_links"):
                    content = requests.get(photo_link).content
                    photo_bytes = io.BytesIO(content)
                    upload = vk_api.VkUpload(self.vk)
                    photo = upload.photo_messages(photos=[photo_bytes])[0]
                    owner_id = photo['owner_id']
                    photo_id = photo['id']
                    self.send_message(user_id=user_id,
                                      attachment=f'photo{owner_id}_{photo_id}')


if __name__ == '__main__':
    bot = VKBot()
    print('Бот запущен')
    while True:
        bot.run()
