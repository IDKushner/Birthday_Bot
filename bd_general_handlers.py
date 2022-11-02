from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, date

from bd_db import db, get_or_create_user, user_birthday_list, update_person, make_all_birthdays_upcoming
from bd_utils import main_keyboard


def start(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    update.message.reply_text(
        f'''Привет, {update.effective_user.first_name}!\nЯ - бот-поздравляшка, буду напоминать о днях рождения твоих друзей и близких\nДавай начнём :)
        ''',
        reply_markup=main_keyboard(), 
    )

def explain(update, context):
    text = '<b> Что я умею: </b>\n\n'
    text += '<b>Запоминать людей:</b> нажми "Добавить" и ответь на вопросы\n'
    text += '<b>Проверять человека в базе:</b> нажми "Проверить" и введи имя человека: если он есть, я выдам тебе всю имеющуюся информацию о нём. Если его нет - скажу об этом\n'
    text += '<b>Изменять</b> любые данные, которые ты вносил при добавлении человека (имя, дату др, интересы и пр.). Для этого нажми "Изменить"\n'
    text += '<b>Удалять людей:</b> нажми "Удалить", введи имя, и я больше тебе о нём не напомню! (Не очень-то и хотелось)\n'
    text += '<b>Показать всех людей, которые есть в базе:</b> для этого нажми "Показать все ДР"'
    update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard()
    )

def wtf(update, context):
    update.message.reply_text('Не понимаю :(')

def talk_to_me(update, context):
    update.message.reply_text('🤖')

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

def check_if_upcoming(user_date):
    d, m, y = list(map(int, user_date.split('.')))
    birthday = date(date.today().year, m, d)
    if birthday > date.today():
        return True
    else:
        return False

def confirm_reminder_date(user_reminder_date):
    try:
        reminder_date = int(user_reminder_date)
    except:
        return 'Количество дней, за которое нужно напомнить о др, должно быть цифрой'

    if reminder_date > 366:
        return 'Нельзя ставить напоминания больше чам за год до др'
    
    return True

def check_upcoming_birthdays(context): 

    for user in db.users.find():
        birthday_list = user_birthday_list(user['user_id'])
        reminder = []
        for person in birthday_list:
            if person != None:
                if person['upcoming_birthday'] == True:
                    d, m, y = list(map(int, person['date'].split('.')))
                    birthday = date(date.today().year, m, d)
                    delta = birthday - date.today()
                    years = (abs(date(y, m, d) - birthday)/365).days
                    if delta.days in set(person['reminder_dates']):
                        for reminder_date in set(person['reminder_dates']):
                            if delta.days - reminder_date == 0:
                                reminder.append([reminder_date, person['name'], person['date'], years])
                                if reminder_date == 0:
                                    person_data = {'name':person['name'], 'field':'upcoming_birthday', 'change':False}
                                    update_person(user['user_id'], person_data)

        if len(reminder) > 0:
            upcoming_birthdays = format_upcoming_birthdays(reminder)
            reminder.clear()
            context.bot.send_message(
                chat_id = user['chat_id'],
                text = upcoming_birthdays,
                parse_mode=ParseMode.HTML 
            )
        
def format_upcoming_birthdays(reminder):
    text = f'<b>Сводка по ближайшим ДР</b>\n'

    sorted_reminder = sorted(reminder, key = lambda x: x[0])

    for person in sorted_reminder:
        reminder_date = person[0]
        name = person[1]
        birthday_date = person[2]
        years = person[3]
        if reminder_date == 0:
            text += f"\n{sorted_reminder.index(person)+1}) {name}: {birthday_date}. Сегодня исполнилось {years}"
        else:
            text += f"\n{sorted_reminder.index(person)+1}) {name}: {birthday_date}. Через {reminder_date} дней исполнится {years}"

    text += f'\n\nЧтобы получить сводку информации о человеке (интересы, подарки и прочее), нажми "<b>Проверить</b>" и введи его имя'

    return text

def if_all_birthdays_are_upcoming(context):
    if date.today().month == 12:
        make_all_birthdays_upcoming()

def send_base(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    birthday_list = user_birthday_list(user['user_id'])
    text = '<b>Все записанные ДР:</b>\n'

    temp = []
    for person in birthday_list:
        if person != None:
            temp.append([person['name'], person['date']])
    
    sorted_base = sorted(temp, key = lambda x: x[0])
    for person in sorted_base:
        text += f"\n{sorted_base.index(person)+1}) {person[0]}: {person[1]}"

    update.message.reply_text(
        text,
        reply_markup=main_keyboard(),
        parse_mode=ParseMode.HTML
    )
