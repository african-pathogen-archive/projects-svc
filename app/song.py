import requests
from config import Config
from flask_jwt_extended import jwt_required

@jwt_required()
def get_song_studies(jwt_token):

    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401

    try:        
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.SONG_API + '/studies/all', headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error creating group: {e}"}, 500
        
@jwt_required()
def create_song_study(payload, jwt_token):

    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401

    try:        
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.SONG_API + '/studies/' + payload.studyId, json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error creating group: {e}"}, 500