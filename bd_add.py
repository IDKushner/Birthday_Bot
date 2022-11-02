from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from bd_db import db, get_or_create_user, save_birthday
from bd_general_handlers import confirm_date, check_if_upcoming, confirm_reminder_date
from bd_utils import main_keyboard, skip_keyboard, return_keyboard, return_to_main

def add_start(update, context):
    update.message.reply_text(
        'Добавим новый др! Сначала введи имя/ФИО человека',
        reply_markup=return_keyboard()
    )
    return 'name'

def add_return(update, context):
    return_to_main(update)
    return ConversationHandler.END

def add_name(update, context):
    name = update.message.text
    if len(name.split()) < 1 or len(name) < 1:
        update.message.reply_text('Пожалуйста, введи имя')
        return 'name'
    else:
        context.user_data['birthday'] = {'name':name}
        update.message.reply_text(
            '''Теперь введи дату др в формате ДД.ММ.ГГГГ (например "29.07.2001")\n<b>Проверь правильность даты:</b> если ты ошибёшься, я не смогу прислать поздравление вовремя''', 
            parse_mode=ParseMode.HTML
        )
        return 'date'

def add_date(update, context):
    date = update.message.text
    date_confirmation = confirm_date(date)
    if date_confirmation != True:
        update.message.reply_text(date_confirmation)
        return 'date'
    else:
        context.user_data['birthday']['date'] = date
        context.user_data['birthday']['upcoming_birthday'] = check_if_upcoming(date)
        reminder_date_keyboard = [['0', '3', '14']]
        update.message.reply_text('Теперь поставь как минимум одно количество дней, за которое тебе надо напомнить о приближающемся др.\nВот пара готовых вариантов: если напоминать день в день, жми "0".',
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(reminder_date_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return 'reminder_dates'

def add_reminder_date(update, context):
    reminder_date = update.message.text
    reminder_date_confirmation = confirm_reminder_date(reminder_date)

    if reminder_date_confirmation != True:
        update.message.reply_text(reminder_date_confirmation)
        return 'reminder_dates'
    else:
        reminder_date = abs(int(reminder_date))

    if reminder_date > 366:
        update.message.reply_text('Нельзя ставить напоминания больше чам за год до др')
        return 'reminder_dates'

    if 'reminder_dates' in context.user_data['birthday']:
        if reminder_date > 31:
            update.message.reply_text('Я-то напомню, но хз, зачем тебе напоминание раньше чем за месяц')
        context.user_data['birthday']['reminder_dates'].append(reminder_date)
    else:
        context.user_data['birthday']['reminder_dates'] = [reminder_date]
    
    update.message.reply_text(
            'Ещё одно напоминание ставим? Если да, напиши ещё. Если нет - нажми "Пропустить"',
            reply_markup=skip_keyboard()
        )
    return 'additional_reminder_dates'

def skip_additional_reminder_dates(update, context):
    update.message.reply_text('''Хочешь ввести интересы этого человека, чтобы не забыть при выборе подарка?\nЕсли хочешь, введи интересы в свободной форме.\nПотом ты сможешь их изменить (но для этого их придётся переписать)''',
        reply_markup=skip_keyboard()
    )
    return 'interests'

def add_interests(update, context):
    context.user_data['birthday']['interests'] = update.message.text
    possible_present_keyboard=[['Пропустить']]
    update.message.reply_text(
        'Введи идеи подарков этому человеку (и мб ссылки на них) или нажми "Пропустить". Ты сможешь изменить идеи, если захочешь',
        reply_markup=ReplyKeyboardMarkup(possible_present_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
    return 'present_name'

def skip_interests(update, context):
    update.message.reply_text(
        'Хочешь ввести идеи подарков этому человеку? Потом ты сможешь их изменить',
        reply_markup=skip_keyboard()
        )
    return 'present_name'

def add_present_name(update, context):
    present=update.message.text
    if len(present) < 5:
        update.message.reply_text('Я не смогу запомнить подарок без хотя бы названия :(\nВведи хотя бы 5 символов')
        return 'present_name'
    else:
        if 'https://' in present:
            split_ind = present.index('https://')
            present = [present[:split_ind-1], present[split_ind:]]

        if 'possible_presents' in context.user_data['birthday']:
            context.user_data['birthday']['possible_presents'].append(present)
        else:
            context.user_data['birthday']['possible_presents'] = [present]
        
        update.message.reply_text(
            'Ещё подарки есть? Если да, напиши ещё. Если нет - нажми "Пропустить"',
            reply_markup=skip_keyboard()
        )
        return 'additional_presents'

def skip_presents(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    save_birthday(user['user_id'], context.user_data['birthday'])

    added_birthday = format_add(context.user_data['birthday'])

    update.message.reply_text(
        added_birthday,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard()
    )
    return ConversationHandler.END

def format_add(birthday):
    text = f'''
    <b>ДР записан </b>\n<b>Имя: </b> {birthday['name']}\n<b>Дата: </b> {birthday['date']}
    '''
    if 'reminder_dates' in birthday:
        text += '\n<b>Количество дней, за которое предупреждать о ДР</b>:'
        for reminder_date in birthday['reminder_dates']:
            text += f'\n{birthday["reminder_dates"].index(reminder_date)+1}) {reminder_date}'
    if 'interests' in birthday:
        text += f'\n<b>Интересы: </b> {birthday["interests"]}'
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
    