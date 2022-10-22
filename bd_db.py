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
    birthday_data['created'] = datetime.today()
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