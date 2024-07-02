import os
import requests
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity


def get_public_key():
    try:
        response = requests.get(Config.EGO_API + '/oauth/token/public_key')
        response.raise_for_status()  
        public_key = response.text
        return public_key
    except requests.exceptions.RequestException as e:
        print(f"Error fetching public key: {e}")
        return None
    
def get_application_token():
    try:
        response = requests.post(Config.EGO_API + f'/oauth/token?client_id=projects-svc&client_secret={Config.PROJECTS_SVC_SECRET}&grant_type=client_credentials')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching application token: {e}")
        return None
    
@jwt_required()
def new_ego_group(payload, jwt_token):

    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401

    try:        
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.EGO_API + '/groups', json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error creating group: {e}"}, 500
        
@jwt_required()
def new_ego_policy(payload, jwt_token):

    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401

    try:        
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.EGO_API + '/policies', json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error creating policy: {e}"}, 500

@jwt_required()
def add_policy_to_group(group_id, policy_id, jwt_token):
    
    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.EGO_API + f'/groups/{group_id}/permissions', json=[{"mask":"WRITE","policyId": policy_id}], headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error adding policy to group: {e}"}, 500
            
@jwt_required()
def add_user_to_group(group_id, user, jwt_token):
    
    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.EGO_API + f'/groups/{group_id}/users', json=[user], headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error adding user to group: {e}"}, 500
        
@jwt_required()
def remove_user_from_group(group_id, user, jwt_token):
    
    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.delete(Config.EGO_API + f'/groups/{group_id}/users/{user}', headers=headers)
        response.raise_for_status()

        return response.json()
    
    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error removing user from group: {e}"}, 500
        
@jwt_required()
def get_ego_group(group_id, jwt_token):
    
    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/groups/{group_id}', headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error getting group: {e}"}, 500
        
@jwt_required()
def get_ego_policy(policy_id, jwt_token):
    
    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/policies/{policy_id}', headers=headers)
        response.raise_for_status()

        return response.json()
    
    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error getting policy: {e}"}, 500
        
@jwt_required()
def get_ego_group_users(group_id, jwt_token):
    
    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/groups/{group_id}/users', headers=headers)
        response.raise_for_status()

        return response.json()
    
    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error getting group users: {e}"}, 500
        
@jwt_required()
def is_user_in_group(group_id, user_id, jwt_token):
    
    if not jwt_token:
        return {'message': 'JWT token is not available'}, 401
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/groups/{group_id}/users', headers=headers)
        response.raise_for_status()

        users = response.json()['resultSet']

        for user in users:
            if user['id'] == user_id:
                return True
            return False
    
    except requests.exceptions.RequestException as e:
        if e.response:
            return e.response.json()
        else:
            return {'message': f"Error checking user in group: {e}"}, 500