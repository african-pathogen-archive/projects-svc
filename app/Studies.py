from flask import current_app
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
import datetime
from models import db, Study, Project
from song import create_song_study, get_song_studies
from ego import new_ego_group, new_ego_policy, add_policy_to_group, add_user_to_group, get_ego_group

class Studies(Resource):

    @jwt_required()
    def get(self):
        studies = Study.query.all()
        studies_list = []
        for study in studies:
            study_data = study.as_dict()
            studies_list.append(study_data)
        return studies_list
    
    @jwt_required()
    def post(self, project_id):

        jwt_token = request.headers.get('Authorization').split()[1]

        # get the project
        project = Project.query.get(project_id)

        if not project:
            return {'message': 'Project not found'}, 404
        
        admin_group = get_ego_group(project.admin_group, jwt_token)

        if not admin_group:
            return {'message': 'Admin group not found'}, 404
        
        project_group_name = admin_group['name'].split('_')[0]

        # is the user a member of the admin group?
        claims = get_jwt()
        if not admin_group['id'] in claims['context']['user']['groups']:
            return {'message': 'You do not have the required permissions to create a study. Looking for ' + admin_group['id']}, 401
        
        data = request.get_json()

        description = data.get('description')
        info = data.get('info')
        name = data.get('name')
        organization = data.get('organization')
        study_id = description.replace(' ', '_').upper()

        if not (study_id):
            return {'message': 'Required Fields: Study ID'}, 400

        # check if the study already exists
        song_studies = get_song_studies(jwt_token)
        if not song_studies:
            return {'message': 'Error getting studies from song'}, 500
        
        for song_study in song_studies:
            if song_study == study_id:
                return {'message': 'Study already exists'}, 400
            
        # create the study in song
        song_study = create_song_study({
            'studyId': study_id,
            'name': name,
            'description': description,
            'info': info,
            'organization': organization
        }, jwt_token)

        if not song_study:
            return {'message': 'Error creating study in song'}, 500
        
        # create a group in EGO for the study
        study_name = name.replace(' ', '_').upper()
        study_name = project_group_name + '-' + study_name

        study_admin_group = new_ego_group({
            "name": study_name + '_ADMIN',
            "description": f"Admin group for {study_id} study",
            "status": "APPROVED"
        }, jwt_token)

        if not study_admin_group:
            return {'message': 'Error creating study group'}, 500
        
        study_member_group = new_ego_group({
            "name": study_name,
            "description": f"Member group for {study_id} study",
            "status": "APPROVED"
        }, jwt_token)

        if not study_member_group:
            return {'message': 'Error creating study group'}, 500
        
        # create admin and member policies
        study_admin_policy = new_ego_policy({
            "name": study_name + '_ADMIN'
        }, jwt_token)

        if not study_admin_policy:
            return {'message': 'Error creating study admin policy'}, 500
        
        study_member_policy = new_ego_policy({
            "name": study_name
        }, jwt_token)

        if not study_member_policy:
            return {'message': 'Error creating study member policy'}, 500
        
        # add the policies to the groups
        add_policy_to_group(study_admin_group['id'], study_admin_policy['id'], jwt_token)
        add_policy_to_group(study_member_group['id'], study_member_policy['id'], jwt_token)
        
        # add the user to the admin group
        admin_user = add_user_to_group(study_admin_group['id'], get_jwt_identity(), jwt_token)

        if not admin_user:
            return {'message': 'Error adding user to group'}, 500
        
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
    def put(self, id):

        pass
    
    @jwt_required()
    def delete(self, id):

       pass