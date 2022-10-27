from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, date

from bd_db import db, get_or_create_user, user_birthday_list
from bd_utils import main_keyboard


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

def wtf(update, context):
    update.message.reply_text('Не понимаю :(')

def confirm_date(user_date):
    divided_date = user_date.split('.')
    if len(divided_date) < 3:
        return 'Ты забыл что-то ввести (ДД, ММ или ГГГГ) или поставил не "." в качестве разделителя'
    if len(divided_date[0]) < 2 or len(divided_date[1]) < 2 or len(divided_date[2]) < 4:
        return 'Ошибка в формате написания. Пожалуйста, введи дату др в формате ДД.ММ.ГГГГ'
    if int(divided_date[1]) > 12:
        return 'Месяц не может быть больше 12'
    try:
        date_ = datetime.strptime(user_date, '%d.%m.%Y')
        if date_.year > date.today().year:
            return 'Нельзя родиться в будущем :('
    except ValueError:
        return 'Номер дня слишком большой для этого месяца (возможно ты вводишь 30-ое февраля)'
    else:
        return True

def check_upcoming_birthdays(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    birthday_list = user_birthday_list(user['user_id'])

    for person in birthday_list:
        if person != None:
            # if person['upcoming_birthday'] == True:
            d, m, y = list(map(int, person['date'].split('.'))) # заменить через strptime
            birthday = date(date.today().year, m, d)
            delta = birthday - date.today()
            years = abs(date(y, m, d) - birthday)/365
            if delta.days == 0:
                if '0_days' in context.user_data['reminder']:
                    context.user_data['reminder']['0_days'].append([person['name'], person['date'], years])
                else:
                    context.user_data['reminder']['0_days'] = [person['name'], person['date'], years]
            elif delta.days == 3 and person['priority'] in {1, 2}:
                if '3_days' in context.user_data['reminder']:
                    context.user_data['reminder']['3_days'].append([person['name'], person['date'], years])
                else:
                    context.user_data['reminder']['3_days'] = [person['name'], person['date'], years]
            elif delta.days == 14 and person['priority'] == 1:
                if '14_days' in context.user_data['reminder']:
                    context.user_data['reminder']['14_days'].append([person['name'], person['date'], years])
                else:
                    context.user_data['reminder']['14_days'] = [person['name'], person['date'], years]

    if len(context.user_data['reminder']) > 0:
        upcoming_birthdays = format_upcoming_birthdays(context.user_data['reminder'])
        context.user_data['reminder'].clear()
        update.message.reply_text(
            upcoming_birthdays,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard()
        )
        # context.bot.send_message(
        #     chat_id = user['chat_id'],
        #     text = 'Хоть что-то работает' # мб затупит т.к. text есть и в функции format_upcoming_birthdays. при ошибке -- заменить
        # )

def format_upcoming_birthdays(reminder):
    text = f'<b>Сводка по ближайшим ДР</b>'
    
    if '0_days' in reminder:
        text += '<b>\nДР сегодня:</b>'
        for person in reminder['0_days']:
            text += f"\n{reminder['0_days'].index(person)}) {person[0]} : {person[1]}. Исполнилось {person[2]}\n"

    if '3_days' in reminder:
        text += '<b>\nДР через 3 дня:</b>'
        for person in reminder['3_days']:
            text += f"\n{reminder['3_days'].index(person)}) {person[0]} : {person[1]}. Исполнится {person[2]}\n"

    if '14_days' in reminder:
        text += '<b>\nДР через 2 недели:</b>'
        for person in reminder['14_days']:
            text += f"\n{reminder['14_days'].index(person)}) {person[0]} : {person[1]}. Исполнилось {person[2]}\n"

    text += f'\n Чтобы получить сводку информации о человеке (интересы, подарки и прочее), нажми "Проверить" и введи его имя'

    return text