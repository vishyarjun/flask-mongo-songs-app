# Backend Developer Assignment

## URL of the application

This application can be run through thr URL `https://localhost:5000`


## API End Points

This application consists of 5 endpoints
1) `GET /songs` - this endpoint returns the songs from the MongoDB. Page and limit can be passed optionally. If not passed page is defaulted to 1 and limit is defaulted to 10

2) `GET /search_songs` - this endpoint enables a search on the songs DB based on title and artist. any matching result will be returned. message parameter is mandatory

3) `GET /difficulty` - this endpoint returns the average difficulty of the songs from the DB. An optional level can be passed which will return the average difficulty only for the level

4) `POST /rating` - This endpoint adds a new rating to any song available in the DB. a valid song_id and rating is required

5) `GET /rating` - This endpoint returns the average, minimum and maximum rating for a given song.

## Error Handling

Different Types of error from the application

- 400 Bad Request


## Installation and Dependency

1. Download and Install Python from [here](https://www.python.org/downloads/)
2. Change the directory to the assignment folder.

3. Setup a Virtual Environment with following command
```
python3 -m venv venv
. venv/bin/activate
```
`Note: If you are using windows use venv\Scripts\activate instead of . venv/bin/activate`

4. Setup the dependencies in the venv using following command
```
pip3 install -r requirements.txt
```

5. To Setup DB, install docker and create a container instance of MongoDB. Follow [this](https://docs.docker.com/get-docker/)  to install Docker

- start the docker and open a new terminal window.
- run `docker run --detach --name songs_db --publish 127.0.0.1:27017:27017 mongo:4.4`
- load the data and create indexes by running below command inside the app directory. Use the same venv terminal from above to run this
```
cd app
python data_load.py
```

while we are inside the app directory, execute the following command.

```
export FLASK_APP = app
export FLASK_ENV = development
flask run
```
`Note: if you are running on a windows environment use SET instead of EXPORT above, example: set FLASK_APP = app`
## Test Locally

There are two ways to test this application locally.
### 1. POSTMAN
- Using end point details, we can run the tests in postman. To install postman click [here](https://www.postman.com/downloads/)

### 2. Pytest
- open a new terminal window and cd to assignment directory
- get into venv using `. venv/bin/activate`
- cd `test` directory in a terminal window inside the project
- Run `pytest api_test.py`

## Scaling for large volume of data and users
- Scaling can be done on both Flask Application and MongoDB to a larger extent
- Flask App can be containeraized and Multiple container instances can be run for flask app using docker compose etc. This will also  ensure our app is not a single point of failure.
- MongoDB supports horizontal scaling using Data Sharding
- Further the API's can be optimized to make it light weight.
- Following are some of the scope of improvements
    - For searching the songs with title and artist, a seperate indexed field can be created with all th keywords from title and artist for each song stored as a list. search can be made against the new field.
    - we can precompute the lowest, highest and average value of rating and only retrieve it when the endpoint is called instead of running the logic on the fly.
    - Averages for difficulty can be precomputed for every level and can be retreived instead of grouping with average.