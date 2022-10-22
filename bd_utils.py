from telegram import ReplyKeyboardMarkup

def main_keyboard():
    return ReplyKeyboardMarkup([
        ['Что я умею', 'Добавить др']
    ])

def skip_keyboard():
    return ReplyKeyboardMarkup([
        ['Пропустить']
    ])