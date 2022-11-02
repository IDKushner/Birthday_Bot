from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from bd_db import db, get_or_create_user, check_person, update_person
from bd_general_handlers import confirm_date, check_if_upcoming, confirm_reminder_date
from bd_utils import main_keyboard, skip_keyboard, make_update_keyboard, return_keyboard, return_to_main

def update_person_start(update, context):
    update.message.reply_text(
        'Изменим информацию о человеке. Введи имя',
        reply_markup=return_keyboard()
    )  # не даёт сделать replykeyboardremove: TypeError: Object of type type is not JSON serializable
    return 'name'


def update_return(update, context):
    return_to_main(update)
    return ConversationHandler.END


def add_name_for_updating(update, context):
    name = update.message.text
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    person = check_person(user['user_id'], name)
    if person: 
        context.user_data['birthday'] = person
        context.user_data['update'] = {'name':name}
        update_keyboard = [['name', 'date', 'reminder_dates', 'interests', 'possible_presents']]
        update.message.reply_text(
            'Есть такой!\nТеперь выбери поле, которое будем обновлять',
            reply_markup=ReplyKeyboardMarkup(update_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return 'field'
    else:
        update.message.reply_text(
            'Не могу обновить данные того, кого его нет в базе :(',
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END


def add_field(update, context):
    context.user_data['update']['field'] = update.message.text
    update.message.reply_text(
            'Напиши новую информацию, которую запишем вместо старой',
            reply_markup=ReplyKeyboardRemove()
        )
    return 'change'


def add_change(update, context):
    change = update.message.text

    if context.user_data['update']['field'] == 'date':
        date_confirmation = confirm_date(change)
        if date_confirmation != True:
            update.message.reply_text(
                date_confirmation
            )
            return 'change'
        else:
            context.user_data['update']['upcoming_birthday'] = check_if_upcoming(change)
    
    if context.user_data['update']['field'] == 'reminder_dates':
        reminder_date_confirmation = confirm_reminder_date(change)
        if reminder_date_confirmation != True:
            update.message.reply_text(reminder_date_confirmation)
            return 'change'
        else:
            if 'change' in context.user_data['update']:
                context.user_data['update']['change'].append(abs(int(change)))

                update.message.reply_text(
                    'Ещё одно напоминание ставим? Если да, напиши ещё. Если нет - нажми "Пропустить"',
                    reply_markup=skip_keyboard()
                )
                return 'update_additional_reminder_dates'
            
            elif 'change' not in context.user_data['update']:
                context.user_data['update']['change'] = [abs(int(change))]
                
                update.message.reply_text(
                    'Ещё одно напоминание ставим? Если да, напиши ещё. Если нет - нажми "Пропустить"',
                    reply_markup=skip_keyboard()
                )
                return 'update_additional_reminder_dates'
    
    if context.user_data['update']['field'] == 'possible_presents' and len(change) < 5:
        update.message.reply_text('Я не смогу запомнить подарок без хотя бы названия :(\nВведи хотя бы 5 символов')
        return 'change'

    else:
        if 'https://' in change:
            split_ind = change.index('https://')
            change = [change[:split_ind-1], change[split_ind:]]

        if context.user_data['update']['field'] == 'possible_presents' and 'change' in context.user_data['update']:
            context.user_data['update']['change'].append(change)

            update.message.reply_text(
                'Ещё подарки есть? Если да, напиши ещё. Если нет - нажми "Пропустить"',
                reply_markup=skip_keyboard()
            )
            return 'update_additional_presents'
        
        elif context.user_data['update']['field'] == 'possible_presents' and 'change' not in context.user_data['update']:
            context.user_data['update']['change'] = [change]
            
            update.message.reply_text(
                'Ещё подарки есть? Если да, напиши ещё. Если нет - нажми "Пропустить"',
                reply_markup=skip_keyboard()
            )
            return 'update_additional_presents'

    if context.user_data['update']['field'] not in {'reminder_dates', 'possible_presents'}:
        context.user_data['update']['change'] = change
        updated_field = context.user_data['update']['field']
        context.user_data['birthday'][updated_field] = change
    
    update.message.reply_text(
        'Обновляем?',
        reply_markup=make_update_keyboard()
    )
    return 'make_update'

def skip_additional_reminder_date(update, context):
    context.user_data['birthday']['reminder_dates'] = context.user_data['update']['change']
    update.message.reply_text(
        'Обновляем?',
        reply_markup=make_update_keyboard()
    )
    return 'make_update'

def update_person_operation(update, context):
    update_person(update.effective_user.id, context.user_data['update'])
    updated_birthday = updated_format(context.user_data['birthday'])
    update.message.reply_text(
            updated_birthday,
            reply_markup=main_keyboard(),
            parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

def skip_update_additional_presents(update, context):
    context.user_data['birthday']['possible_presents'] = context.user_data['update']['change']
    update.message.reply_text(
        'Обновляем?',
        reply_markup=make_update_keyboard()
    )
    return 'make_update'

def updated_format(birthday):
    text = f'''
    <b>Обновлённые данные </b>\n<b>Имя: </b> {birthday['name']}\n<b>Дата: </b> {birthday['date']}
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