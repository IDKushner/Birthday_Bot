from telegram import ReplyKeyboardMarkup

def main_keyboard():
    return ReplyKeyboardMarkup([
        ['Что я умею', 'Добавить', 'Проверить', 'Удалить', 'Изменить']
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