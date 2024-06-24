import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@db/projects'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_ALGORITHM = 'RS256'

    SONG_API = 'https://apasong.sanbi.ac.za'
    EGO_API = 'https://apaego.sanbi.ac.za/api'

    PROJECT_SCOPE = 'PROJECTS-SERVICE.WRITE'
    PATHOGEN_SCOPE = 'PROJECTS-SERVICE.WRITE'

    