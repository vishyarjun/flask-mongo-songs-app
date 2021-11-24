# mongo.py

from flask import Flask, abort
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

#DB Configurations -- TODO Move this to a config file
app.config['MONGO_DBNAME'] = 'songs_db'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/songs_db'

mongo = PyMongo(app)



@app.route('/songs', methods=['GET'])
def get_all_songs():
    songs = mongo.db.songs
    #return bad request incase if the int conversion fails for limit or page
    try:
        limit = int(request.args.get('limit',default=10))
        page = int(request.args.get('page',default=1))
    except:
        return 'Bad Request', 400

    if limit<1 or page<1 or limit>=1000000000 or page >=1000000000:
        return 'Bad Request', 400
    output = []
    # every page starts with the index which is next to last index of previous page
    skips=(page-1)*limit
    for s in songs.find().skip(skips).limit(limit):
        output.append({
	'artist': s['artist'],
	'title': s['title'],
	'difficulty': s['difficulty'],
	'level': s['level'],
	'released': s['released']
})
    return jsonify({'result' : output}) if output else jsonify({'result': 'no results found'})


@app.route('/search_songs', methods=['GET'])
def search_songs():
    songs = mongo.db.songs
    message=request.args.get('message',None)
    if not message:
        return {"result":"Please provide a search message"}, 400
    
    #TODO for a faster text search result, store the keys of title and artist in an array field and index the array field
    # build a pipeline with case insensitive search option for title and artist
    pipeline={"$or":[{"title":{"$regex":message,"$options":"i"}},{"artist":{"$regex":message,'$options':'i'}}]}
    output = []
    for s in songs.find(pipeline):
                output.append({
	'artist': s['artist'],
	'title': s['title'],
	'difficulty': s['difficulty'],
	'level': s['level'],
	'released': s['released']
})
    return jsonify({'result' : output}) if output else jsonify({'result': 'no results found'})
    


@app.route('/difficulty', methods=['GET'])
def get_avg_difficulty():
    songs = mongo.db.songs
    try:
        ip = request.args.get('level')
        level = int(ip) if ip else None
    except:
        return 'Bad Request', 400
    if level and (level<=0 or level>=100000000):
        return 'Bad Request', 400
    #build a pipeline for aggregation when level is valid or when level is not passed as a param
    pipeline =[
        {
        "$match": {"level": {'$eq': level}}
    },
    {
        "$group":
            {
                "_id":"_id",
                "average": {"$avg": "$difficulty"}
            }
    }
    

    ] if level else [{
        "$group":
            {
                "_id": "_id",
                "average": {"$avg": "$difficulty"}
            }
    }
    ]
    for result in songs.aggregate(pipeline):
        return jsonify({'result': round(result['average'],2)})
    return jsonify({'result': 'No data exist'})



@app.route('/rating', methods=['POST'])
def add_rating():
    songs = mongo.db.songs
    song_id = request.args.get('song_id', None)
    #when rating is not an int or song_id is not valid, it should return a bad request
    try:
        rate = int(request.args.get('rating', None))
        s=[song for song in songs.find({'_id': ObjectId(song_id)})][0]
    except:
        return 'Bad request',400
    if not song_id or not rate or not s or not 1<=rate<=5:
        return 'Bad request',400
    else:
        #for the first entry add a new rating array or append to an existing array
        if s.get('rating'):
            songs.update_one({'_id': ObjectId(song_id)},{ '$push':{'rating': rate}})
        else:
            songs.update_one({'_id': ObjectId(song_id)},{'$push':{'rating': {'$each':[rate]}}})
        return jsonify({'result' : 'success'})

@app.route('/rating', methods=['GET'])
def get_rating():
    songs = mongo.db.songs
    song_id = request.args.get('song_id', None)
    if not song_id:
        return 'Bad request',400
    try:
        s=[song for song in songs.find({'_id': ObjectId(song_id)})][0].get('rating')
    except:
        return 'Bad request',400      
    if s:
        #sort the array after pulling it from DB. To scale it further, store the sorted array directly in DB.
        s.sort()
        #on a sorted array 0th index is the lowest and -1 st index is highest
        output = {'average': round(sum(s)/len(s),2), 'lowest':s[0],'highest':s[-1]}
        return jsonify({'result' : output})
    else:
        return jsonify({'result':'rating not available'})


if __name__ == '__main__':
    app.run(debug=True)