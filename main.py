from cls_vk_bot import VkBot

if __name__ == '__main__':
    bot = VkBot()
    print('Бот запущен')
    while True:
        bot.run()
