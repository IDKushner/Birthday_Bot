from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from bd_db import db, get_or_create_user, save_birthday
from bd_utils import main_keyboard, skip_keyboard


def start(update, context):
    print('вызван /start')
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    update.message.reply_text(
        f'''Привет, {update.effective_user.first_name}!\nЯ - бот-поздравляшка, буду напоминать о днях рождения твоих друзей и близких\nДавай начнём :)
        ''',
        reply_markup=main_keyboard(),
    )

def explain(update, context):
    update.message.reply_text(
        '''<b> Что я умею: </b>\n<b>Запоминать дни рождения:</b> нажми "Добавить др", введи данные и приоритет (1, 2 или 3). В зависимости от приоритета человека я буду напоминать тебе о его др день в день (1, 2, 3), за 3 дня (1, 2) и за 2 недели (1)\n<b>Удалять дни рождения:</b> нажми "Удалить др", введи имя, и я больше тебе о нём не напомню! (Не очень-то и хотелось)
        ''',
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard()
    )

def add_start(update, context):
    update.message.reply_text(
        'Добавим новый др! Сначала введи имя/ФИО человека',
        reply_markup=ReplyKeyboardRemove()
    )
    return 'name'

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
    divided_date = date.split('.')
    if len(divided_date) < 3 or len(divided_date[0]) < 2 or len(divided_date[1]) < 2 or len(divided_date[2]) < 4:
        update.message.reply_text('Пожалуйста, введи дату др в формате ДД.ММ.ГГГГ')
        return 'date'
    else:
        context.user_data['birthday']['date'] = date
        priority_keyboard = [['1', '2', '3']]
        update.message.reply_text('''Теперь поставь приоритет:\nО <b> 1м приоретете </b>буду напоминать за 14, 3 и 0 дней до др.\nО <b> 2м приоретете </b>за 3 и 0 дней\nО <b> 3м приоретете </b>только за 0 дней (день в день)''',
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(priority_keyboard, one_time_keyboard=True))
        return 'priority'

def add_priority(update, context):
    context.user_data['birthday']['priority'] = int(update.message.text)
    update.message.reply_text('''Хочешь ввести интересы этого человека, чтобы не забыть при выборе подарка?\nЕсли хочешь, введи интересы в свободной форме.\nПотом ты сможешь их изменить (но для этого их придётся переписать)''',
        reply_markup=skip_keyboard()
    )
    return 'interests'

def skip_interests(update, context):
    possible_presents_keyboard=[['Пропустить', 'Ввести идеи подарков']]
    update.message.reply_text(
        'Хочешь ввести идеи подарков этому человеку? Потом ты сможешь их изменить',
        reply_markup=ReplyKeyboardMarkup(possible_presents_keyboard, one_time_keyboard=True)
        )
    return 'present_name'

def add_interests(update, context):
    context.user_data['birthday']['interests'] = update.message.text
    possible_present_keyboard=[['Пропустить', 'Ввести идеи подарков']]
    update.message.reply_text(
        'Хочешь ввести идеи подарков этому человеку? Потом ты сможешь их изменить',
        reply_markup=ReplyKeyboardMarkup(possible_present_keyboard, one_time_keyboard=True)
        )
    return 'present_name'

def add_present_name(update, context):
    # update.message.reply_text('Введи название возможного подарка и ссылку на него (опционально)')
    present=update.message.text
    if len(present) < 3:
        update.message.reply_text('Я не смогу запомнить подарок без названия :(')
        return 'present_name'
    else:
        if 'https://' in present:
            present.replace('https://', '!!!https://')
            present = present.split('!!!')

        if 'possible_presents' in context.user_data['birthday']:
            context.user_data['birthday']['possible_presents'].append(present)
        else:
            context.user_data['birthday']['possible_presents'] = [present]
        
        additional_presents_keyboard = [['Да', 'Нет']]
        update.message.reply_text(
            'Ещё подарки есть?',
            reply_markup=ReplyKeyboardMarkup(additional_presents_keyboard, one_time_keyboard=True)
        )
        return 'additional_presents'

def skip_presents(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    save_birthday(user['user_id'], context.user_data['birthday'])

    added_birthday = format(context.user_data['birthday'])

    update.message.reply_text(
        added_birthday,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard()
    )
    return ConversationHandler.END

def format(birthday):
    text = f'''
    <b>ДР записан </b>\n<b>Имя: </b> {birthday['name']}\n<b>Дата: </b> {birthday['date']}\n<b>Приоритет: </b> {birthday['priority']}
    '''
    if 'interests' in birthday:
        text += f'<b>Интересы: </b> {birthday["interests"]}'
    if 'possible_presents' in birthday:
        text += f'<b>Идеи подарков: </b>'
        for present in birthday["possible_presents"]:
            text += f'\n{birthday["possible_presents"].index(present) + 1}) {present[0]} (ссылка: {present[1]})'

    return text

def wtf(update, context):
    update.message.reply_text('Не понимаю :(')

# def add_present_link(update, context):
#     update.message.reply_text('Введите ссылку на подарок')
#     link = update.message.text
#     if link[0:5] != 'https':
#         update.message.reply_text('Пожалуйста, введи ссылку')
#         return 'present_link'
#     else:
#         if 'possible_presents' in context.user_data['birthday']:
#             context.user_data['birthday']['possible_presents'].append({present:link})

    # if link == update.message.entities.URL or НЕ ЗНАЮ, КАК ЭТО РЕАЛИЗОВАТЬ
