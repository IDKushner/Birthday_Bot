from telegram import ReplyKeyboardMarkup

def main_keyboard():
    return ReplyKeyboardMarkup([
        ['Что я умею', 'Добавить'], 
        ['Проверить', 'Изменить'],
        ['Удалить', 'Показать все ДР']
    ],
    resize_keyboard=True)

def skip_keyboard():
    return ReplyKeyboardMarkup([['Пропустить']],
    resize_keyboard=True
    )

def make_update_keyboard():
    return ReplyKeyboardMarkup([['Обновляем!']],
    resize_keyboard=True
    )

def return_keyboard():
    return ReplyKeyboardMarkup([['Назад']],
    resize_keyboard=True
    )

def return_to_main(update):
    return update.message.reply_text(
        'Упс, возвращаемся',
        reply_markup=main_keyboard()
        )