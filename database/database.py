#(©)CodeXBotz




import pymongo, os
from config import DB_URI, DB_NAME


dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]


user_data = database['users']
config_data = database['config']




async def present_user(user_id : int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return


async def add_admin(user_id: int):
    """Promote a user to admin in the database."""
    user_data.update_one({'_id': user_id}, {'$set': {'is_admin': True}}, upsert=True)

async def remove_admin(user_id: int):
    """Demote a user from admin in the database."""
    user_data.update_one({'_id': user_id}, {'$set': {'is_admin': False}})

async def get_admin_list():
    """Get a list of all admins from the database."""
    admin_docs = user_data.find({'is_admin': True})
    return [doc['_id'] for doc in admin_docs]

# Force subscription management functions
async def set_force_sub_channel(channel_id: str):
    """Set the force subscription channel in the database."""
    config_data.update_one({}, {'$set': {'force_sub_channel': channel_id}}, upsert=True)

async def get_force_sub_channel():
    """Retrieve the current force subscription channel from the database."""
    config = config_data.find_one()
    return config.get('force_sub_channel') if config else None

async def remove_force_sub_channel():
    """Remove the force subscription channel from the database."""
    config_data.update_one({}, {'$unset': {'force_sub_channel': ""}})
