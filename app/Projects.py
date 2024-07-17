from flask import current_app, abort
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
from models import db, Pathogen, Project, Study
from ego import new_ego_group, new_ego_policy, add_policy_to_group, add_user_to_group, remove_user_from_group, get_application_token, user_in_group, user_has_permission, get_ego_group_users

class Projects(Resource):

    def get(self, id=None, project_id=None):

        if project_id:
            # Logic for GET /api/projects/<project_id>/studies
            
            project = Project.query.get(project_id)

            if not project:
                abort(404, 'Project not found')
            
            studies = Study.query.filter_by(project_id=project_id).all()
            studies_list = [study.as_dict() for study in studies]

            return studies_list
        
        elif id:
            # Logic for GET /api/projects/<id>

            project = Project.query.get(id)

            if not project:
                abort(404, 'Project not found')
            
            project_data = project.as_dict()
            studies = Study.query.filter_by(project_id=id).all()
            project_data['study_count'] = len(studies)

            pathogen = Pathogen.query.get(project.pathogen_id)
            project_data['pathogen'] = pathogen.as_dict()

            return project_data
        else:
            # Logic for GET /api/projects

            projects = Project.query.all()
            project_list = []
            for project in projects:
                project_data = project.as_dict()

                project_data = project.as_dict()
                studies = Study.query.filter_by(project_id=project.id).all()
                project_data['study_count'] = len(studies)

                pathogen = Pathogen.query.get(project.pathogen_id)
                project_data['pathogen'] = pathogen.as_dict()

                project_list.append(project_data)
            return project_list
    
    @jwt_required()
    def post(self, id=None, user_id=None):

        if id and user_id:
            # Logic for POST /api/projects/<id>/users/<user_id>
            # Adds a user to a project admin group

            project = Project.query.get(id)

            if not project:
                abort(404, 'Project not found')
            
            admin_user_id = get_jwt_identity()

            jwt_token = get_application_token()

            allowed = user_in_group(project.admin_group, admin_user_id, jwt_token)

            if not allowed:
                abort(401, 'You do not have the required permissions to add a user to this project')

            try:
                group_user = add_user_to_group(project.admin_group, user_id, jwt_token)
            except Exception as e:
                raise e

            return group_user, 201

        else:
            # Logic for POST /api/projects
            # Creates a new project

            policy = current_app.config['PROJECT_SCOPE'].split('.')[0]
            mask = current_app.config['PROJECT_SCOPE'].split('.')[1]
            user_id = get_jwt_identity()

            if not user_has_permission(user_id, policy, mask):
                abort(401, "You do not have the required permissions to create a new project")

            data = request.get_json()

            title = data.get('title')
            pid = data.get('pid')
            pathogen_id = data.get('pathogen_id')
            description = data.get('description')

            if not title or not pid or not pathogen_id:
                abort(400, "Required Fields: Title, PID, Pathogen ID")

            # check if pathogen exists
            pathogen = Pathogen.query.get(pathogen_id)
            if not pathogen:
                abort(404, 'Pathogen not found')

            jwt_token = get_application_token()

            admin_group_title = 'P-' + pid.replace(' ', '_').upper() + '_ADMIN'
            admin_policy_title = 'P-' + pid.replace(' ', '_').upper()

            project = Project.query.filter_by(pid=pid).first()
            if project:
                abort(400, 'Project with PID already exists')

            # EGO WORK

            try:
                admin_group = new_ego_group({
                    "name": admin_group_title,
                    "description": f"Admin group for {pid} project",
                    "status": "APPROVED"
                }, jwt_token)
            except Exception as e:
                raise e

            try:
                admin_policy = new_ego_policy({
                    "name": admin_policy_title
                }, jwt_token)
            except Exception as e:
                raise e
            
            try:
                add_policy_to_group(admin_group['id'], admin_policy['id'], jwt_token)
            except Exception as e:
                raise e

            try:
                admin_user = add_user_to_group(admin_group['id'], user_id, jwt_token)
            except Exception as e:
                raise e
            
            new_project = Project(
                title = title,
                pid = pid,
                pathogen_id = pathogen_id,
                admin_group = admin_group['id'],
                description = description,
                owner = user_id
            )

            try:
                db.session.add(new_project)
                db.session.commit()

                return new_project.as_dict(), 201
            
            except Exception as e:
                raise e
                
        

    @jwt_required()
    def put(self, id):

        # Logic for PUT /api/projects/<id>
        # Updates a project

        policy = current_app.config['PROJECT_SCOPE'].split('.')[0]
        mask = current_app.config['PROJECT_SCOPE'].split('.')[1]

        if not user_has_permission(get_jwt_identity(), policy, mask):
            abort(401, "You do not have the required permissions to update this project")

        data = request.get_json()

        title = data.get('title')
        pid = data.get('pid')
        pathogen_id = data.get('pathogen_id')
        description = data.get('description')
        

        project = db.session.get(Project, id)
        if not project:
            abort(404, 'Project not found')

        if title:
            project.title = title
        if pid:
            project.pid = pid
        if pathogen_id:
            project.pathogen_id = pathogen_id
        if description:
            project.description = description

        existing_project = Project.query.filter_by(pid=pid).first()
        if existing_project and existing_project.id != project.id:
            abort(400, 'Project with PID already exists')

        db.session.commit()
        return project.as_dict(), 200
    
    @jwt_required()
    def delete(self, id, user_id=None):

        if id and user_id:
            # Logic for DELETE /api/projects/<id>/users/<user_id>
            # Removes a user from a project admin group

            policy = current_app.config['PROJECT_SCOPE'].split('.')[0]
            mask = current_app.config['PROJECT_SCOPE'].split('.')[1]

            if not user_has_permission(get_jwt_identity(), policy, mask):
                abort(401, "You do not have the required permissions to update this project")

            project = Project.query.get(id)

            if not project:
                abort(404, 'Project not found')

            try:
                project_users = get_ego_group_users(project.admin_group, get_application_token())['resultSet']
            except Exception as e:
                raise e

            user_count = len(project_users)

            if user_count < 2:
                abort(400, 'Cannot remove the last user from a project')
            
            jwt_token = get_application_token()

            try:
                group_user = remove_user_from_group(project.admin_group, user_id, jwt_token)
            except Exception as e:
                raise e

            
            return {'message': 'User removed from project'}, 204


        else:
            # Logic for DELETE /api/projects/<id>
            # Deletes a project
            
            policy = current_app.config['PROJECT_SCOPE'].split('.')[0]
            mask = current_app.config['PROJECT_SCOPE'].split('.')[1]

            if not user_has_permission(get_jwt_identity(), policy, mask):
                abort(401, "You do not have the required permissions to delete this project")

            # check if project has studies
            studies = Study.query.filter_by(project_id=id).all()

            active_studies = [study for study in studies if not study.deleted_at]
            if active_studies:
                abort(400, 'Cannot delete a project with active studies')
            

            project = db.session.get(Project, id)
            if not project:
                abort(404, 'Project not found')
           
            project.deleted_at = datetime.datetime.now()
            
            db.session.commit()
            return {'message': 'Project deleted'}, 204