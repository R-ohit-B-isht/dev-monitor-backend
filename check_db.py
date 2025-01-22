from pymongo import MongoClient
from pprint import pprint

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client.devin_tasks

# Print available collections
# print('Collections:', db.list_collection_names())

# Check schedule limits
print('\nSchedule Limits:')
for limit in db.tasks.find():
    print(limit)

# Check settings
# print('\nSettings:')
# for setting in db.settings.find():
#     pprint(setting)
