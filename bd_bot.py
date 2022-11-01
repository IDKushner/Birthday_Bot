import logging
import pytz
from datetime import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import bd_Settings

from bd_general_handlers import start, explain, wtf, talk_to_me, check_upcoming_birthdays, if_all_birthdays_are_upcoming, send_base
from bd_add import add_start, add_return, add_name, add_date, add_reminder_date, skip_additional_reminder_dates, skip_interests, add_interests, skip_presents, add_present_name
from bd_check_or_delete import check_person_start, check_return, check_person_operation, delete_person_start, delete_return, delete_person_operation
from bd_update import update_person_start, update_return, add_name_for_updating, add_field, add_change, skip_additional_reminder_date, update_person_operation, skip_update_additional_presents

logging.basicConfig(filename='bd_bot.log', level=logging.INFO)


def main():
    bot = Updater(bd_Settings.API_KEY)

    jq = bot.job_queue

    run_daily_time = time(0, 0, tzinfo=pytz.timezone('Europe/Moscow'))
    jq.run_daily(check_upcoming_birthdays, run_daily_time) 

    run_monthly_time = time(12, 0, tzinfo=pytz.timezone('Europe/Moscow'))
    jq.run_monthly(if_all_birthdays_are_upcoming, run_monthly_time, 31)

    dp = bot.dispatcher

    add_birthday = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Добавить)$'), add_start)
        ],
        states={
            'name': [
                MessageHandler(Filters.regex('^(Назад)$'), add_return),
                MessageHandler(Filters.text, add_name)
            ],
            'date': [MessageHandler(Filters.text, add_date)],
            'reminder_dates': [MessageHandler(Filters.text, add_reminder_date)],
            'additional_reminder_dates': [
                MessageHandler(Filters.regex('^(Пропустить)$'), skip_additional_reminder_dates),
                MessageHandler(Filters.text, add_reminder_date)
            ],
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
            'check_person':[
                MessageHandler(Filters.regex('^(Назад)$'), check_return),
                MessageHandler(Filters.text, check_person_operation)
            ]
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
            'delete_person':[
                MessageHandler(Filters.regex('^(Назад)$'), delete_return),
                MessageHandler(Filters.text, delete_person_operation)
            ]
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
            'name':[
                MessageHandler(Filters.regex('^(Назад)$'), update_return),
                MessageHandler(Filters.text, add_name_for_updating)
            ],
            'field':[MessageHandler(Filters.regex('^(name|date|reminder_dates|interests|possible_presents)$'), add_field)],
            'change':[MessageHandler(Filters.text, add_change)],
            'update_additional_reminder_dates': [
                MessageHandler(Filters.regex('^(Пропустить)$'), skip_additional_reminder_date),
                MessageHandler(Filters.text, add_change)
            ],
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

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.regex('^(Что я умею)$'), explain))
    dp.add_handler(MessageHandler(Filters.regex('^(Показать все ДР)$'), send_base))
    
    dp.add_handler(add_birthday)
    dp.add_handler(check_person)
    dp.add_handler(delete_person)
    dp.add_handler(update_person)

    dp.add_handler(MessageHandler(
                Filters.text | Filters.video | Filters.photo | Filters.document | Filters.location, talk_to_me
            ))
    
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()