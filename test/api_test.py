import requests
import json
import random
import string
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
db = client['songs_db']
songs = db['songs']

# API 1 - Get Songs with Page and Limit
def test_songs_get_200():
    response = requests.get("http://localhost:5000/songs?limit=100&page=1")
    bdy = response.json()
    assert response.status_code == 200 and bdy

def test_songs_no_limit_no_page_200():
    response = requests.get("http://localhost:5000/songs")
    bdy = response.json()
    assert response.status_code == 200 and bdy

def test_songs_result_lte_limit_200():
    response = requests.get("http://localhost:5000/songs?limit=5&page=1")
    bdy = response.json()['result']
    assert response.status_code == 200 and len(bdy)<=5

def test_songs_negative_limit_400():
    response = requests.get("http://localhost:5000/songs?limit=-5&page=1")
    assert response.status_code == 400

def test_songs_negative_page_400():
    response = requests.get("http://localhost:5000/songs?limit=5&page=-1")
    assert response.status_code == 400

def test_songs_text_val_400():
    response = requests.get("http://localhost:5000/songs?limit=abc&page=abc")
    assert response.status_code == 400

def test_songs_symbols_400():
    response = requests.get("http://localhost:5000/songs?limit=abc&page=abc")
    assert response.status_code == 400

def test_songs_big_values_400():
    response = requests.get("http://localhost:5000/songs?limit=100000000000000000&page=10000000000000000")
    assert response.status_code == 400



# API 2 - Average Difficulty for levels

def test_difficulty_no_level_200():
    response = requests.get("http://localhost:5000/difficulty")
    bdy = response.json()["result"]
    assert response.status_code == 200 and bdy>0


def test_difficulty_with_level_200():
    response = requests.get("http://localhost:5000/difficulty?level=9")
    bdy = response.json()["result"]
    assert response.status_code == 200 and bdy>0

def test_difficulty_negative_level_400():
    response = requests.get("http://localhost:5000/difficulty?level=-9")
    assert response.status_code == 400

def test_difficulty_high_level_400():
    response = requests.get("http://localhost:5000/difficulty?level=1234567898765")
    assert response.status_code == 400

def test_difficulty_text_level_400():
    response = requests.get("http://localhost:5000/difficulty?level=abcdf")
    assert response.status_code == 400

def test_difficulty_spl_char_level_400():
    response = requests.get("http://localhost:5000/difficulty?level=.,?{}[]")
    assert response.status_code == 400


def test_difficulty_level_not_exist_200():
    response = requests.get("http://localhost:5000/difficulty?level=1023")
    bdy = response.json()['result']
    assert response.status_code == 200 and bdy=="No data exist"



# API 3 Search Songs by Title or Artist

def test_search_songs_title_match_200():
    response = requests.get("http://localhost:5000/search_songs?message=new")
    bdy = response.json()['result']
    assert response.status_code == 200 and len(bdy)>0


def test_search_songs_artist_match_200():
    response = requests.get("http://localhost:5000/search_songs?message=You")
    bdy = response.json()['result']
    assert response.status_code == 200 and len(bdy)>0

def test_search_songs_both_match_200():
    response = requests.get("http://localhost:5000/search_songs?message=the")
    bdy = response.json()['result']
    assert response.status_code == 200 and len(bdy)>0


def test_search_songs_case_insensitivity_200():
    response = requests.get("http://localhost:5000/search_songs?message=CAN'T")
    bdy = response.json()['result']
    assert response.status_code == 200 and len(bdy)>0

def test_search_long_text_match_200():
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(1000))
    response = requests.get("http://localhost:5000/search_songs?message="+result_str)
    bdy = response.json()['result']
    assert response.status_code == 200 and bdy=="no results found"

def test_search_spl_chars_200():
    response = requests.get("http://localhost:5000/search_songs?message=./,:{}p")
    bdy = response.json()['result']
    assert response.status_code == 200 and bdy=="no results found"

def test_search_empty_message_400():
    response = requests.get("http://localhost:5000/search_songs?message=")
    bdy = response.json()['result']
    assert response.status_code == 400 and bdy=="Please provide a search message"

def test_search_empty_message2_400():
    response = requests.get("http://localhost:5000/search_songs")
    bdy = response.json()['result']
    assert response.status_code == 400 and bdy=="Please provide a search message"


# API 4 - Add rating to a song

def test_push_rating_valid_200():
    song=songs.insert_one({'artist': ''.join(random.choice("abcdef") for i in range(15)),
	'title': ''.join(random.choice("abcdef") for i in range(15)),
	'difficulty': 10,
	'level': 9,
	'released': "2012-05-11",
    'rating':[2]
    })
    res=[song for song in songs.find({'_id': ObjectId(song.inserted_id)})][0]['rating']
    url ="http://localhost:5000/rating?song_id={}&rating=3".format(song.inserted_id)
    response=requests.post(url)
    res2=[song for song in songs.find({'_id': ObjectId(song.inserted_id)})][0]['rating']
    assert response.status_code == 200 and len(res2)>len(res)

def test_new_rating_valid_200():
    song=songs.insert_one({'artist': ''.join(random.choice("abcdef") for i in range(15)),
	'title': ''.join(random.choice("abcdef") for i in range(15)),
	'difficulty': 10,
	'level': 9,
	'released': "2012-05-11"
    })
    url ="http://localhost:5000/rating?song_id={}&rating=3".format(song.inserted_id)
    response=requests.post(url)
    res2=[song for song in songs.find({'_id': ObjectId(song.inserted_id)})][0]['rating']
    assert response.status_code == 200 and len(res2)==1


def test_rating_invalid_song_id_400():
    url ="http://localhost:5000/rating?song_id={}&rating=3".format(1)
    response=requests.post(url)
    assert response.status_code == 400

def test_rating_invalid_rating_id_400():
    song=songs.insert_one({'artist': ''.join(random.choice("abcdef") for i in range(15)),
	'title': ''.join(random.choice("abcdef") for i in range(15)),
	'difficulty': 10,
	'level': 9,
	'released': "2012-05-11"
    })
    url ="http://localhost:5000/rating?song_id={}&rating=-1".format(song.inserted_id)
    response=requests.post(url)
    assert response.status_code == 400


def test_rating_invalid_rating_id2_400():
    song=songs.insert_one({'artist': ''.join(random.choice("abcdef") for i in range(15)),
	'title': ''.join(random.choice("abcdef") for i in range(15)),
	'difficulty': 10,
	'level': 9,
	'released': "2012-05-11"
    })
    url ="http://localhost:5000/rating?song_id={}&rating=abc".format(song.inserted_id)
    response=requests.post(url)
    assert response.status_code == 400

#API 5 - Return rating

def test_get_rating_valid_200():
    song=songs.insert_one({'artist': ''.join(random.choice("abcdef") for i in range(15)),
	'title': ''.join(random.choice("abcdef") for i in range(15)),
	'difficulty': 10,
	'level': 9,
	'released': "2012-05-11",
    'rating': [1,3,4,1,3,2,3,4,5,4]
    })
    url="http://localhost:5000/rating?song_id={}".format(song.inserted_id)
    response=requests.get(url)
    assert response.status_code==200 and response.json()['result']['lowest']==1

def test_get_no_rating_200():
    song=songs.insert_one({'artist': ''.join(random.choice("abcdef") for i in range(15)),
	'title': ''.join(random.choice("abcdef") for i in range(15)),
	'difficulty': 10,
	'level': 9,
	'released': "2012-05-11"
    })
    url="http://localhost:5000/rating?song_id={}".format(song.inserted_id)
    response=requests.get(url)
    assert response.status_code==200 and response.json()['result']=="rating not available"

def test_rating_invaid_song_400():
    url="http://localhost:5000/rating?song_id={}".format(1)
    response=requests.get(url)
    assert response.status_code==400
