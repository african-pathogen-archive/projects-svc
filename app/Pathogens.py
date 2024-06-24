from flask import current_app
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt
import datetime
from models import db, Pathogen

class Pathogens(Resource):
    def get(self):
        pathogens = Pathogen.query.all()
        pathogen_list = []
        for pathogen in pathogens:
            pathogen_data = pathogen.as_dict()
            pathogen_list.append(pathogen_data)
        return pathogen_list
    

    @jwt_required()
    def post(self):
        data = request.get_json()
        
        common_name = data.get('common_name')
        scientific_name = data.get('scientific_name')
        schema = data.get('schema')
        schema_version = data.get('schema_version')

        if not (common_name or scientific_name):
            return {'message': 'Required Fields: Common name and Scientific name'}, 400
       

        claims = get_jwt()
        if current_app.config['PATHOGEN_SCOPE'] in claims['context']['scope']:

            pathogen = Pathogen.query.filter_by(common_name=common_name).first()
            if pathogen:
                return {'message': 'Pathogen already exists'}, 400
            
            new_pathogen = Pathogen(
                common_name = common_name,
                scientific_name = scientific_name,
                schema = schema,
                schema_version = schema_version
            )

            db.session.add(new_pathogen)
            db.session.commit()

            return new_pathogen.as_dict(), 201
        else:
            return {'message': 'You do not have the required permissions to create a pathogen'}, 401
    

    @jwt_required()
    def put(self, id):
        data = request.get_json()
        
        common_name = data.get('common_name')
        scientific_name = data.get('scientific_name')
        schema = data.get('schema')
        schema_version = data.get('schema_version')

        pathogen = db.session.get(Pathogen, id)
        if not pathogen:
            return {'message': 'Pathogen not found'}, 404

        if common_name:
            pathogen.common_name = common_name
        if scientific_name:
            pathogen.scientific_name = scientific_name
        if schema:
            pathogen.schema = schema
        if schema_version:
            pathogen.schema_version = schema_version

        claims = get_jwt()
        if current_app.config['PATHOGEN_SCOPE'] in claims['context']['scope']:
            db.session.commit()

            return pathogen.as_dict(), 200
        else:
            return {'message': 'You do not have the required permissions to update this pathogen'}, 401

    
    @jwt_required()
    def delete(self, id):

        pathogen = db.session.get(Pathogen, id)
        if not pathogen:
            return {'message': 'Pathogen not found'}, 404
        
        pathogen.deleted_at = datetime.datetime.now()
        
        claims = get_jwt()
        if current_app.config['PATHOGEN_SCOPE'] in claims['context']['scope']:
            db.session.commit()
            return {'message': 'Pathogen deleted'}, 204
        else:
            return {'message': 'You do not have the required permissions to delete this pathogen'}, 401