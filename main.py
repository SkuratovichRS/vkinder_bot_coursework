from cls_vk_bot import VKBot

if __name__ == '__main__':
    bot = VKBot()
    print('Бот запущен')
    while True:
        bot.run()
