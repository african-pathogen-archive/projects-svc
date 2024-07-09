from flask import current_app, abort
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
import datetime
from models import db, Pathogen, Project
from ego import user_has_permission
class Pathogens(Resource):
    def get(self, id=None):

        if id:
            # Logic for GET /api/pathogens/<id>

            pathogen = Pathogen.query.get(id)
            if not pathogen:
                abort(404, 'Pathogen not found')
            projects = Project.query.filter_by(pathogen_id=pathogen.id).all()
            pathogen_data = pathogen.as_dict()
            pathogen_data['project_count'] = len(projects)

            return pathogen_data
        else:
            # Logic for GET /api/pathogens

            pathogens = Pathogen.query.all()
            pathogen_list = []
            for pathogen in pathogens:
                pathogen_data = pathogen.as_dict()
                projects = Project.query.filter_by(pathogen_id=pathogen.id).all()
                pathogen_data['project_count'] = len(projects)
                pathogen_list.append(pathogen_data)

            return pathogen_list

    @jwt_required()
    def post(self):
        # Logic for POST /api/pathogens

        policy = current_app.config['PATHOGEN_SCOPE'].split('.')[0]
        mask = current_app.config['PATHOGEN_SCOPE'].split('.')[1]
        
        if not user_has_permission(get_jwt_identity(), policy, mask):
            abort(401, "You do not have the required permissions to create a new pathogen")
        
        data = request.get_json()
        
        common_name = data.get('common_name')
        scientific_name = data.get('scientific_name')
        schema = data.get('schema')
        schema_version = data.get('schema_version')

        if not common_name or not scientific_name:
            raise BadRequest("Required Fields: Common name and Scientific name")

        pathogen = Pathogen.query.filter_by(common_name=common_name).first()
        if pathogen:
            abort(409, "Pathogen already exists")
        
        new_pathogen = Pathogen(
            common_name = common_name,
            scientific_name = scientific_name,
            schema = schema,
            schema_version = schema_version
        )

        db.session.add(new_pathogen)
        db.session.commit()

        return new_pathogen.as_dict(), 201

    @jwt_required()
    def put(self, id):
        # Logic for PUT /api/pathogens/<id>

        policy = current_app.config['PATHOGEN_SCOPE'].split('.')[0]
        mask = current_app.config['PATHOGEN_SCOPE'].split('.')[1]

        if not user_has_permission(get_jwt_identity(), policy, mask):
            abort(401, "You do not have the required permissions to update this pathogen")

        data = request.get_json()
        
        common_name = data.get('common_name')
        scientific_name = data.get('scientific_name')
        schema = data.get('schema')
        schema_version = data.get('schema_version')

        pathogen = db.session.get(Pathogen, id)
        if not pathogen:
            abort(404, "Pathogen not found")

        if common_name:
            pathogen.common_name = common_name
        if scientific_name:
            pathogen.scientific_name = scientific_name
        if schema:
            pathogen.schema = schema
        if schema_version:
            pathogen.schema_version = schema_version

        db.session.commit()

        return pathogen.as_dict(), 200

    
    @jwt_required()
    def delete(self, id):
        # Logic for DELETE /api/pathogens/<id>

        policy = current_app.config['PATHOGEN_SCOPE'].split('.')[0]
        mask = current_app.config['PATHOGEN_SCOPE'].split('.')[1]

        if not user_has_permission(get_jwt_identity(), policy, mask):
            abort(401, "You do not have the required permissions to delete this pathogen")

        pathogen = db.session.get(Pathogen, id)
        if not pathogen:
            abort(404, "Pathogen not found")
        
        pathogen.deleted_at = datetime.datetime.now()

        policy = current_app.config['PATHOGEN_SCOPE'].split('.')[0]
        mask = current_app.config['PATHOGEN_SCOPE'].split('.')[1]

        db.session.commit()
        return {'message': 'Pathogen deleted'}, 204