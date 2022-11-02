from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from bd_db import db, get_or_create_user, check_person, delete_person
from bd_utils import main_keyboard, return_keyboard, return_to_main

def check_person_start(update, context):
    update.message.reply_text(
        'Введите имя человека, наличие которого хотите проверить',
        reply_markup=return_keyboard()
    ) # почему-то если сюда добавить ReplyKeyboardRemove, то функция будет выдавать ошибку TypeError: Object of type type is not JSON serializable
    return 'check_person'

def check_return(update, context):
    return_to_main(update)
    return ConversationHandler.END

def check_person_operation(update, context):
    name = update.message.text
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    person = check_person(user['user_id'], name)
    if person:
        checked_birthday = format_checked(person)
        update.message.reply_text(
            checked_birthday,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Не знаю такого :(',
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END

def format_checked(birthday):
    text = f'''
    <b>Есть такой!</b>\n<b>Имя: </b> {birthday['name']}\n<b>Дата: </b> {birthday['date']}
    '''
    if 'reminder_dates' in birthday:
        text += '\n<b>Количество дней, за которое предупреждать о ДР</b>:'
        for reminder_date in birthday['reminder_dates']:
            text += f'\n{birthday["reminder_dates"].index(reminder_date)+1}) {reminder_date}'
    if 'interests' in birthday:
        text += f'<b>\nИнтересы: </b> {birthday["interests"]}'
    if 'possible_presents' in birthday:
        text += f'\n<b>Идеи подарков: </b>'
        for present in birthday["possible_presents"]:
            if type(present) == list:
                if len(present) > 1:
                    text += f'\n{birthday["possible_presents"].index(present)+1}) {present[0]} (ссылка: {present[1]})'
                else:
                    text += f'\n{birthday["possible_presents"].index(present)+1}) {present[0]}'
            if type(present) == str:
                text += f'\n{birthday["possible_presents"].index(present)+1}) {present}'

    return text

def delete_person_start(update, context):
    update.message.reply_text(
        'Удалим человека!\nВведи имя',
        reply_markup=return_keyboard()
    )
    return 'delete_person'

def delete_return(update, context):
    return_to_main(update)
    return ConversationHandler.END

def delete_person_operation(update, context):
    name = update.message.text
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    if check_person(user['user_id'], name) != False:
        delete_person(user['user_id'], name)
        update.message.reply_text(
            f'{name} удалён (Так ему и надо)',
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            f'{name} нет в базе :(',
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END