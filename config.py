import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@db/projects'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    PUBLIC_KEY_URL = 'https://apaego.sanbi.ac.za/api/oauth/token/public_key'
    JWT_ALGORITHM = 'RS256'

    SONG_API = 'https://apasong.sanbi.ac.za'

    PROJECT_GROUP = '3cf1fe66-d27f-4fa2-9c26-2ae095db9c56'
    PATHOGEN_GROUP = '3cf1fe66-d27f-4fa2-9c26-2ae095db9c56'

    