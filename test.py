import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
import os


class VKBot:
    TOKEN = 'vk1.a.1Ju1eKhG7yqQZ8RgAqfuAjUEEA8zO-DTcHM8FZkqhpyzkEPlqyhlwJNZyRam-eZl_EVNGd68qBNXcEbXQwvC2_gz6ZxW4VDgpAnXefMQ6532OPs4xwIifVnmCDUZaK4wZGeZ2n2 8rxEFiCWSM4CQy153hnKbzPdnQRI_217US9vFpxv2iY1ab-PNpj9dJmddxQro69uldNYgOk8xddLWXw'

    def __init__(self):
        # Авторизация в VK
        self.vk_session = vk_api.VkApi(token=self.TOKEN)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)

    def send_message(self, user_id, message=None, keyboard=None):
        self.vk.messages.send(
            user_id=user_id,
            random_id=0,
            keyboard=keyboard,
            message=message
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

    # Основной цикл бота
    def run(self):
        # Ожидаем ответ пользователя
        text, user_id = self.interface()
        self.start_create_keyboard()

        if text == 'настроить фильтры поиска':
            self.filter_city(user_id)

        elif text == 'поиск':
            pass

        elif text == 'Посмотреть настроенные фильтры':
            pass

        elif text == 'Сбросить фильтры':
            pass


if __name__ == '__main__':
    bot = VKBot()
    bot.run()
    print('Бот запущен')
