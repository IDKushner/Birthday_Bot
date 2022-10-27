import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import bd_Settings
from bd_general_handlers import start, explain, wtf, check_upcoming_birthdays
from bd_add import add_start, add_name, add_date, add_priority, skip_interests, add_interests, skip_presents, add_present_name
from bd_check_or_delete import check_person_start, check_person_operation, delete_person_start, delete_person_operation
from bd_update import update_person_start, add_name_for_updating, add_field, add_change, skip_update_additional_presents, update_person_operation

logging.basicConfig(filename='bd_bot.log', level=logging.INFO)


def main():
    bot = Updater(bd_Settings.API_KEY)

    jq = bot.job_queue
    # jq.run_repeating(check_upcoming_birthdays, interval=60) 

    # должна работать, если есть хотя бы 1 человек, за кем надо следить
    # daily проверяет наличие хотя бы 1 человека в списке тех, у кого не было др, а потом проверяет др

    dp = bot.dispatcher

    add_birthday = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Добавить)$'), add_start)
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
                MessageHandler(Filters.text, add_present_name)
            ],
            'additional_presents': [
                MessageHandler(Filters.regex('^(Пропустить)$'), skip_presents),
                MessageHandler(Filters.text, add_present_name)
            ],
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

    check_person = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Проверить)$'), check_person_start)],
        states={
            'check_person':[MessageHandler(Filters.text, check_person_operation)]
        },
        fallbacks=[
            MessageHandler(
                Filters.text | Filters.video | Filters.photo | Filters.document | Filters.location, wtf
            )
        ] 
    )

    delete_person = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Удалить)$'), delete_person_start)],
        states = {
            'delete_person':[MessageHandler(Filters.text, delete_person_operation)]
        },
        fallbacks=[
            MessageHandler(
                Filters.text | Filters.video | Filters.photo | Filters.document | Filters.location, wtf
            )
        ]
    )

    update_person = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Изменить)$'), update_person_start)
        ],
        states= {
            'name':[MessageHandler(Filters.text, add_name_for_updating)],
            'field':[MessageHandler(Filters.regex('^(name|date|priority|interests|possible_presents)$'), add_field)],
            'change':[MessageHandler(Filters.text, add_change)],
            'update_additional_presents': [
                MessageHandler(Filters.regex('^(Пропустить)$'), skip_update_additional_presents),
                MessageHandler(Filters.text, add_change)
            ],
            'make_update':[MessageHandler(Filters.regex('^(Обновляем!)$'), update_person_operation)]
        },
        fallbacks=[
            MessageHandler(
                Filters.text | Filters.video | Filters.photo | Filters.document | Filters.location, wtf
            )
        ]
    )

    dp.add_handler(CommandHandler('start', start)) # pass_job_queue=True ??
    dp.add_handler(MessageHandler(Filters.regex('^(Что я умею)$'), explain))
    
    dp.add_handler(add_birthday)
    dp.add_handler(check_person)
    dp.add_handler(delete_person)
    dp.add_handler(update_person)
    
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()