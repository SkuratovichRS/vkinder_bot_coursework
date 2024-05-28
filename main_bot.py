from typing import Any

import requests
import io
import vk_api
import configparser
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from api_vk import VkApi


class VKBot:
    TOKEN = 'vk1.a.1Ju1eKhG7yqQZ8RgAqfuAjUEEA8zO-DTcHM8FZkqhpyzkEPlqyhlwJNZyRam-eZl_EVNGd68qBNXcEbXQwvC2_gz6ZxW4VDgpAnXefMQ6532OPs4xwIifVnmCDUZaK4wZGeZ2n2 8rxEFiCWSM4CQy153hnKbzPdnQRI_217US9vFpxv2iY1ab-PNpj9dJmddxQro69uldNYgOk8xddLWXw'

    def __init__(self):
        # Авторизация в VK
        self.vk_session = vk_api.VkApi(token=self.TOKEN)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.config = configparser.ConfigParser()
        self.config.read("token.ini")
        self.api = VkApi(self.config['TOKEN']['vk_token'])

    def send_message(self, user_id, message=None, keyboard=None, attachment=None):
        self.vk.messages.send(
            user_id=user_id,
            random_id=0,
            keyboard=keyboard,
            message=message,
            attachment=attachment
        )

    def interface(self):
        # Ожидаем ответ пользователя
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()
                user_id = event.user_id
                return text, user_id

    # Функция для создания клавиатуры бота
    def start_create_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_button('Настроить фильтры поиска', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()  # Добавление новой строки
        keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
        return keyboard.get_keyboard()

    # Функция для создания клавиатуры с кнопками "Парень" и "Девушка"
    def create_keyboard_gender(self):
        keyboard = VkKeyboard()
        keyboard.add_button('Парень', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Девушка', color=VkKeyboardColor.POSITIVE)
        return keyboard.get_keyboard()

    def handle_gender_selection(self, event):
        # Получаем текст нажатой кнопки
        selected_gender = event.object.text

        # Обрабатываем выбор пользователя
        if selected_gender == 'Парень':
            # Действия при выборе "Парень"
            print("Пользователь выбрал 'Парень'")
        elif selected_gender == 'Девушка':
            # Действия при выборе "Девушка"
            print("Пользователь выбрал 'Девушка'")
        else:
            # Обработка неожиданного результата
            print("Неизвестный выбор:", selected_gender)

    def buttons_filter_male_or_female(self, user_id, city, age):
        # print(city)
        # print(age)
        event, user_id = self.interface()
        keyboard = self.create_keyboard_gender()
        self.send_message(user_id, 'Выберите желаемый пол:', keyboard)
        self.handle_gender_selection(event)

    def filter_age(self, user_id, city):
        # print(user_id)
        # print(city)
        self.send_message(user_id, 'Напишите желаемый возраст:')
        # Ожидаем ответ пользователя
        age, user_id = self.interface()
        self.buttons_filter_male_or_female(user_id, city, age)

    def filter_city(self, user_id):
        self.send_message(user_id, 'Напишите название города:')
        # Ожидаем ответ пользователя
        city, user_id = self.interface()
        self.filter_age(user_id, city)

    def search(self, city: str, age: int, sex: str,
               count: int, user_id: Any, age_range=5) -> None:
        age_from, age_to = age - age_range, age + age_range
        sex_id = 0
        if sex == "Женщина":
            sex_id = 1
        elif sex == "Мужчина":
            sex_id = 2
        self.api.store_pairs_data(city, sex_id, age_from, age_to, count)
        self.show_pair(user_id)

    def show_pair(self, user_id):
        user = self.api.get_pair_from_storage()
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

    # Основной цикл бота
    def run(self):
        # Ожидаем ответ пользователя
        text, user_id = self.interface()
        self.start_create_keyboard()

        if text == 'настроить фильтры поиска':
            self.filter_city(user_id)

        elif text == 'поиск':
            self.search("Москва", 25, "Женщина", 3, user_id)
        elif text == 'дальше':
            if self.api.users_storage:
                self.show_pair(user_id)
            else:
                msg = 'Вы посмотрели все пары, нажмите поиск для генерации новых'
                self.send_message(user_id, msg)

        elif text == 'Посмотреть настроенные фильтры':
            pass

        elif text == 'Сбросить фильтры':
            pass


if __name__ == '__main__':
    bot = VKBot()
    print('Бот запущен')
    bot.run()
