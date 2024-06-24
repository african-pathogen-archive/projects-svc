from flask import current_app
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
import datetime
from models import db, Project
from ego import new_ego_group, new_ego_policy, add_policy_to_group, add_user_to_group

class Projects(Resource):

    @jwt_required()
    def get(self):
        projects = Project.query.all()
        project_list = []
        for project in projects:
            project_data = project.as_dict()
            project_list.append(project_data)
        return project_list
    
    @jwt_required()
    def post(self):

        data = request.get_json()

        title = data.get('title')
        pid = data.get('pid')
        pathogen_id = data.get('pathogen_id')
        description = data.get('description')

        if not (title or pid or pathogen_id):
            return {'message': 'Required Fields: Title, PID, Pathogen ID, Admin Group'}, 400


        claims = get_jwt()
        if current_app.config['PROJECT_SCOPE'] in claims['context']['scope']:

            jwt_token = request.headers.get('Authorization').split()[1]

            admin_group_title = title.replace(' ', '_').upper() + '_ADMIN'
            admin_policy_title = title.replace(' ', '_').upper()


            # EGO WORK

            admin_group = new_ego_group({
                "name": admin_group_title,
                "description": f"Admin group for {title} project",
                "status": "APPROVED"
            }, jwt_token)

            if not admin_group:
                return {'message': 'Error creating admin group'}, 500

            admin_policy = new_ego_policy({
                "name": admin_policy_title
            }, jwt_token)
            
            if not admin_policy:
                return {'message': 'Error creating admin policy'}, 500
            else:
                add_policy_to_group(admin_group['id'], admin_policy['id'], jwt_token)

            admin_user = add_user_to_group(admin_group['id'], get_jwt_identity(), jwt_token)

            if not admin_user:
                return {'message': 'Error adding user to group'}, 500
            

            project = Project.query.filter_by(title=title).first()
            if project:
                return {'message': 'Project already exists'}, 400
            
            new_project = Project(
                title = title,
                pid = pid,
                pathogen_id = pathogen_id,
                admin_group = admin_group['id'],
                description = description,
                owner = get_jwt_identity()
            )

            db.session.add(new_project)
            db.session.commit()

            return new_project.as_dict(), 201
    
        else:
            return {'message': 'You do not have the required permissions to create a project'}, 401
        

    @jwt_required()
    def put(self, id):

        data = request.get_json()

        title = data.get('title')
        pid = data.get('pid')
        pathogen_id = data.get('pathogen_id')
        description = data.get('description')
        

        project = db.session.get(Project, id)
        if not project:
            return {'message': 'Project not found'}, 404

        if title:
            project.title = title
        if pid:
            project.pid = pid
        if pathogen_id:
            project.pathogen_id = pathogen_id
        if description:
            project.description = description

        claims = get_jwt()
        if current_app.config['PROJECT_SCOPE'] in claims['context']['scope']:
            db.session.commit()
            return project.as_dict(), 200
        else:
            return {'message': 'You do not have the required permissions to update this project'}, 401
    
    @jwt_required()
    def delete(self, id):

        project = db.session.get(Project, id)
        if not project:
            return {'message': 'Project not found'}, 404
        
        project.deleted_at = datetime.datetime.now()
        
        claims = get_jwt()
        if current_app.config['PROJECT_SCOPE'] in claims['context']['scope']:
            db.session.commit()
            return {'message': 'Project deleted'}, 204
        else:
            return {'message': 'You do not have the required permissions to delete this project'}, 401    