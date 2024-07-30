from flask import abort
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
from models import db, Study, Project
from song import create_song_study, get_song_studies, get_song_study
from ego import new_ego_group, new_ego_policy, add_policy_to_group, add_user_to_group, get_ego_group, get_ego_group_users, remove_user_from_group, get_application_token, user_in_group

class Studies(Resource):
    
    def get(self, study_id=None):

        if study_id:
            # Logic for GET /api/studies/<study_id>

            study = Study.query.get(study_id)

            if not study:
                abort(404, 'Study not found')
            
            jwt_token = get_application_token()
            
            study_admin_group = get_ego_group_users(study.admin_group, jwt_token)
            study_member_group = get_ego_group_users(study.member_group, jwt_token)

            study_details = get_song_study(study.study, jwt_token)

            study_data = study.as_dict()

            study_data['admins'] = study_admin_group
            study_data['members'] = study_member_group
            study_data['name'] = study_details['name']
            study_data['description'] = study_details['description']
            study_data['organization'] = study_details['organization']

            return study_data

        else:
            # Logic for GET /api/studies

            jwt_token = get_application_token()

            studies = Study.query.all()
            studies_list = []
            for study in studies:
                study_details = get_song_study(study.study, jwt_token)
                study_data = study.as_dict()
                
                study_data['name'] = study_details['name']
                study_data['description'] = study_details['description']
                study_data['organization'] = study_details['organization']

                studies_list.append(study_data)
            return studies_list
    
    @jwt_required()
    def post(self, study_id=None, user_id=None, role=None):

        if study_id and user_id and role:
            # Logic for POST /api/studies/<study_id>/users/<user_id>/<role>
            # Adds a user to a study admin group or member group
            
            study = Study.query.get(study_id)

            if not study:
                abort(404, 'Study not found')
                
            admin_user_id = get_jwt_identity()

            jwt_token = get_application_token()

            if not user_in_group(study.admin_group, admin_user_id, jwt_token):
                abort(401, 'You do not have the required permissions to manage users for this study')

            if role == 'admin':
                group_user = add_user_to_group(study.admin_group, user_id, jwt_token)
            elif role == 'member':
                group_user = add_user_to_group(study.member_group, user_id, jwt_token)

            if not group_user:
                abort(500, 'Error adding user to group')

            return group_user, 201



        else:
            # Logic for POST /api/studies
            data = request.get_json()

            project_id = data.get('project_id')

            admin_user_id = get_jwt_identity()

            jwt_token = get_application_token()

            # get the project
            project = Project.query.get(project_id)

            if not project:
                abort(404, 'Project not found')

            try:        
                admin_group = get_ego_group(project.admin_group, jwt_token)
            except Exception as e:
                raise e
            
            project_group_name = admin_group['name'].split('_')[0]
            
            if not user_in_group(project.admin_group, admin_user_id, jwt_token):
                abort(401, 'You do not have the required permissions to create a study')
            
            description = data.get('description')
            info = data.get('info')
            name = data.get('name')
            organization = data.get('organization')
            study_id = name.replace(' ', '_').upper()

            if not (study_id):
                abort(400, 'Study ID is required')

            # check if the study already exists
            try:
                song_studies = get_song_studies(jwt_token)
            except Exception as e:
                raise e
            
            for song_study in song_studies:
                if song_study == study_id:
                    abort(409, 'Study already exists')
                
            # create the study in song
            try:
                song_study = create_song_study({
                    'studyId': study_id,
                    'name': name,
                    'description': description,
                    'info': info,
                    'organization': organization
                }, jwt_token)
            except Exception as e:
                raise e

            # create a group in EGO for the study
            study_name = name.replace(' ', '_').upper()
            study_name = project_group_name + '-' + study_name

            try:
                study_admin_group = new_ego_group({
                    "name": study_name + '_ADMIN',
                    "description": f"Admin group for {study_id} study",
                    "status": "APPROVED"
                }, jwt_token)
            except Exception as e:
                raise e
            
            try:
                study_member_group = new_ego_group({
                    "name": study_name,
                    "description": f"Member group for {study_id} study",
                    "status": "APPROVED"
                }, jwt_token)
            except Exception as e:
                raise e
            
            # create admin and member policies
            try:
                study_admin_policy = new_ego_policy({
                    "name": study_name + '_ADMIN'
                }, jwt_token)
            except Exception as e:
                raise e

            try:
                study_member_policy = new_ego_policy({
                    "name": study_name
                }, jwt_token)
            except Exception as e:
                raise e
            
            # add the policies to the groups
            try:
                add_policy_to_group(study_admin_group['id'], study_admin_policy['id'], jwt_token)
                add_policy_to_group(study_member_group['id'], study_member_policy['id'], jwt_token)
            except Exception as e:
                raise e
            
            # add the user to the admin group
            try:
                admin_user = add_user_to_group(study_admin_group['id'], admin_user_id, jwt_token)
            except Exception as e:
                raise e
            
            # add the study to the project
            new_study = Study(
                study = study_id,
                project_id = project_id,
                admin_group = study_admin_group['id'],
                member_group = study_member_group['id']
            )

            db.session.add(new_study)
            db.session.commit()

            return new_study.as_dict(), 201
    
    @jwt_required()
    def delete(self, study_id=None, user_id=None):
        if study_id and user_id:
            # Logic for DELETE /api/studies/<study_id>/users/<user_id>
            # Removes a user from a study admin group or member group

            study = Study.query.get(study_id)

            if not study:
                abort(404, 'Study not found')
            
            admin_user_id = get_jwt_identity()

            jwt_token = get_application_token()
            
            if user_in_group(study.admin_group, admin_user_id, jwt_token) == False:
                abort(401, 'You do not have the required permissions to manage users of a study')

            # user can be in either admin or member group check both

            group_user = remove_user_from_group(study.admin_group, user_id, jwt_token)

            if not group_user:
                group_user = remove_user_from_group(study.member_group, user_id, jwt_token)

                if not group_user:
                    abort(500, 'Error removing user from group')
                
            return group_user, 204

        else:

            study = db.session.get(Study, study_id)
            if not study:
                return {'message': 'Study not found'}, 404
            
            study.deleted_at = datetime.datetime.now()

            admin_user_id = get_jwt_identity()

            jwt_token = get_application_token()

            if not user_in_group(study.admin_group, admin_user_id, jwt_token):
                return {'message': 'You do not have the required permissions to delete this study'}, 401
            
            db.session.commit()
            return {'message': 'Study deleted'}, 204