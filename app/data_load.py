import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['songs_db']
coll = db['songs']

with open('songs.json') as f:
    file_data = json.load(f)
coll.insert_many(file_data)

coll.create_index([("title","text"), ("artist","text")])

client.close()
print("data inserted and indexes created")