from pymongo import MongoClient
import bd_Settings
from datetime import datetime

client = MongoClient(bd_Settings.MONGO_LINK)
db = client[bd_Settings.MONGO_DB]

def get_or_create_user(db, effective_user, chat_id):
    user = db.users.find_one({'user_id':effective_user.id})
    if not user:
        user = {
            'user_id': effective_user.id,
            'user_name': effective_user.first_name,
            'user_surname': effective_user.last_name,
            'username': effective_user.username,
            'chat_id': chat_id
        }
        db.users.insert_one(user)
    return user

def save_birthday(user_id, birthday_data):
    user = db.users.find_one({"user_id": user_id})
    if not 'birthday_list' in user:
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'birthday_list': [birthday_data]}}
    )
    else:
        db.users.update_one(
            {'_id': user['_id']},
            {'$push': {'birthday_list': birthday_data}}
    )

def user_birthday_list(user_id):
    # Монго выдаёт объект класса Cursor
    # итерируем его через эту функцию, чтобы получить нормальный список словарей
    unfiltered_user_birthdays_data = db.users.find({'user_id':user_id}, {'birthday_list':1, '_id':0})
   
    for i in unfiltered_user_birthdays_data:
        user_birthday_list = i['birthday_list']
    
    return user_birthday_list

def check_person(user_id, name):
    birthday_list = user_birthday_list(user_id)
    
    for person in birthday_list:
        if person != None:
            if person['name'] == name:
                return person
    return False

def delete_person(user_id, name):
    birthday_list = user_birthday_list(user_id)
    
    for person in birthday_list:
        if person != None:
            if person['name'] == name:
                delete_ind = 'birthday_list.' + str(birthday_list.index(person))
                db.users.update_one({'user_id':user_id}, {'$unset': {delete_ind:'name'}})
    return False

def update_person(user_id, user_data):
    birthday_list = user_birthday_list(user_id)

    for person in birthday_list:
        if person != None:
            if person['name'] == user_data['name']:
                update_ind = 'birthday_list' + '.' + str(birthday_list.index(person)) + '.' + user_data['field']
                if 'upcoming_birthday' in user_data:
                    upcoming_ind = 'birthday_list' + '.' + str(birthday_list.index(person)) + '.upcoming_birthday'
                    db.users.update_one(
                        {'user_id':user_id}, 
                        {'$set': {upcoming_ind:user_data['upcoming_birthday']}}
                    )
                db.users.update_one({'user_id':user_id}, {'$set': {update_ind:user_data['change']}})
    return False

def make_all_birthdays_upcoming():
    for user in db.users.find():
        birthday_list = user_birthday_list(user['user_id'])
        for person in birthday_list:
            if person != None:
                upcoming_ind = 'birthday_list' + '.' + str(birthday_list.index(person)) + '.upcoming_birthday'
                db.users.update_one(
                    {'user_id':user['user_id']}, 
                    {'$set': {upcoming_ind:True}}
                )