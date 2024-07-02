import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    db_host = os.getenv('DB_HOST', 'db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'projects')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = bool(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS'))
    
    JWT_ALGORITHM = 'RS256'

    SONG_API = os.getenv('SONG_API', 'https://apasong.sanbi.ac.za')
    EGO_API = os.getenv('EGO_API', 'https://apaego.sanbi.ac.za/api')

    PROJECTS_SVC_SECRET = os.getenv('PROJECTS_SVC_SECRET', 'projects-svc-secret')

    PROJECT_SCOPE = os.getenv('PROJECT_SCOPE', 'PROJECTS-SERVICE.WRITE')
    PATHOGEN_SCOPE = os.getenv('PATHOGEN_SCOPE', 'PROJECTS-SERVICE.WRITE')

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')