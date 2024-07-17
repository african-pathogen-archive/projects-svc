import os
import requests
from requests.exceptions import RequestException, HTTPError
from config import Config
from flask_jwt_extended import jwt_required

def get_public_key():
    try:
        response = requests.get(Config.EGO_API + '/oauth/token/public_key')
        response.raise_for_status()  
        public_key = response.text
        return public_key
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
    
def get_application_token():
    try:
        response = requests.post(Config.EGO_API + f'/oauth/token?client_id=projects-svc&client_secret={Config.PROJECTS_SVC_SECRET}&grant_type=client_credentials')
        response.raise_for_status()
        return response.json()['access_token']
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
    
@jwt_required()
def new_ego_group(payload, jwt_token):

    if not jwt_token:
        raise Exception('JWT token is not available', 401)

    try:        
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.EGO_API + '/groups', json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def new_ego_policy(payload, jwt_token):

    if not jwt_token:
        raise Exception('JWT token is not available', 401)

    try:        
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.EGO_API + '/policies', json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err

@jwt_required()
def add_policy_to_group(group_id, policy_id, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.EGO_API + f'/groups/{group_id}/permissions', json=[{"mask":"WRITE","policyId": policy_id}], headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err


@jwt_required()
def add_user_to_group(group_id, user, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(Config.EGO_API + f'/groups/{group_id}/users', json=[user], headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def remove_user_from_group(group_id, user, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.delete(Config.EGO_API + f'/groups/{group_id}/users/{user}', headers=headers)
        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            # If no JSON, return status code and reason
            return {'status_code': response.status_code, 'reason': response.reason}
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def get_ego_group(group_id, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/groups/{group_id}', headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def get_ego_policy(policy_id, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/policies/{policy_id}', headers=headers)
        response.raise_for_status()

        return response.json()
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def get_ego_group_users(group_id, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/groups/{group_id}/users', headers=headers)
        response.raise_for_status()

        return response.json()
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def user_in_group(group_id, user_id, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/groups/{group_id}/users', headers=headers)
        response.raise_for_status()

        users = response.json()['resultSet']

        in_group = False

        for user in users:
            if user['id'] == user_id:
                in_group = True
            
        return in_group
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def user_has_permission(user_id, policy_name, mask):

    jwt_token = get_application_token()

    if not jwt_token:
        raise Exception('JWT token is not available', 401)

    has_permission = False
    user_in_policy = False

    try:
        policy_id = get_policy_id(policy_name, jwt_token)
    except Exception as e:
        raise e

    try:
        policy_users = get_policy_users(policy_id, jwt_token)['resultSet']
    except Exception as e:
        raise e

    for user in policy_users:
        if user['id'] == user_id and user['mask'] == mask:
            has_permission = True
            user_in_policy = True
    
    if not user_in_policy:

        try:
            policy_groups = get_policy_groups(policy_id, jwt_token)['resultSet']
        except Exception as e:
            raise e

        for group in policy_groups:
            if group['mask'] == mask:
                group_users = get_ego_group_users(group['id'], jwt_token)['resultSet']
                for user in group_users:
                    if user['id'] == user_id:
                        has_permission = True

    return has_permission




@jwt_required()
def get_policy_id(policy_name, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/policies', headers=headers)
        response.raise_for_status()

        policies = response.json()['resultSet']

        policy_id = None

        for policy in policies:
            if policy['name'] == policy_name:
                policy_id = policy['id']

        if not policy_id:
            return {'message': 'Policy not found'}, 404

        return policy_id
                                   
        
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def get_policy_users(policy_id, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/policies/{policy_id}/users', headers=headers)
        response.raise_for_status()

        return response.json()
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
        
@jwt_required()
def get_policy_groups(policy_id, jwt_token):
    
    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(Config.EGO_API + f'/policies/{policy_id}/groups', headers=headers)
        response.raise_for_status()

        return response.json()
    
    except HTTPError as http_err:
        raise http_err 
    except RequestException as req_err:
        raise req_err
    
@jwt_required()
def get_ego_users():
    jwt_token = get_application_token()

    if not jwt_token:
        raise Exception('JWT token is not available', 401)
    
    all_users = []
    offset = 0
    limit = 20

    try:
        while True:
            headers = {'Authorization': f'Bearer {jwt_token}'}
            params = {'offset': offset, 'limit': limit}
            response = requests.get(Config.EGO_API + '/users', headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            all_users.extend(data["resultSet"])
            offset += limit

            if offset >= data["count"]:
                break

            all_users = [user for user in all_users if user['status'] == 'APPROVED']
        
        return all_users
    
    except HTTPError as http_err:
        raise http_err
    except RequestException as req_err:
        raise req_err