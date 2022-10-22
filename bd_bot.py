import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import bd_Settings
from bd_handlers import start, explain, add_start, add_name, add_date, add_priority, skip_interests 
from bd_handlers import add_interests, skip_presents, add_present_name, wtf

logging.basicConfig(filename='bd_bot.log', level=logging.INFO)


def main():
    bot = Updater(bd_Settings.API_KEY)

    jq = bot.job_queue
    # jq.run_repeating(send_hello, interval=5) -- должна работать, если есть хотя бы 1 человек, за кем надо следить
    # daily проверяет наличие хотя бы 1 человека в списке тех, у кого не было др, а потом проверяет др

    dp = bot.dispatcher

    add_birthday = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Добавить др)$'), add_start)
        ],
        states={
            'name': [MessageHandler(Filters.text, add_name)],
            'date': [MessageHandler(Filters.text, add_date)],
            'priority': [MessageHandler(Filters.regex('^(1|2|3)$'), add_priority)],
            'interests': [
                MessageHandler(Filters.regex('^(Пропустить)$'), skip_interests),
                MessageHandler(Filters.text, add_interests)
            ],
            'present_name': [
                MessageHandler(Filters.regex('^(Пропустить)$'), skip_presents),
                MessageHandler(Filters.regex('^(Ввести идеи подарков)$'), add_present_name)
            ],
            'additional_presents': [
                MessageHandler(Filters.regex('^(Нет)$'), skip_presents),
                MessageHandler(Filters.regex('^(Да)$'), add_present_name)
            ]
            # 'present_link':[
            #     MessageHandler(Filters.regex('^(Пропустить)$'), skip_presents),
            #     MessageHandler(Filters.regex('^(Ввести ссылку на подарок)$'), add_present_link)
            # ]
        },
        fallbacks=[
            MessageHandler(
                Filters.text | Filters.video | Filters.photo | Filters.document | Filters.location, wtf
            )
        ] 
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.regex('^(Что я умею)$'), explain))
    
    dp.add_handler(add_birthday)
    
    
    
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()