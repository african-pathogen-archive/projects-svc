from json import JSONEncoder
from flask import Flask, request, jsonify
from flask_restful import Api as RestfulApi, Resource, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful_swagger_2 import Api as SwaggerApi, swagger
from flask_cors import CORS
from config import Config
from models import db, Project, Pathogen, Study
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import datetime
import requests


app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"]}})

db.init_app(app)
migrate = Migrate(app, db)

api = SwaggerApi(app, api_version='0.1', api_spec_url='/swagger')

SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "SANBI Projects"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if not hasattr(app, 'json_encoder'):
    app.json_encoder = JSONEncoder

def get_public_key():
    try:
        response = requests.get(app.config['PUBLIC_KEY_URL'])
        response.raise_for_status()  
        public_key = response.text
        return public_key
    except requests.exceptions.RequestException as e:
        print(f"Error fetching public key: {e}")
        return None

app.config['JWT_PUBLIC_KEY'] = get_public_key()

jwtm = JWTManager(app)

# Proxy to SONG API. Fix this.
@app.route('/api/schemas/', methods=['GET'])
def get_schemas():
    try:
        response = requests.get(app.config['SONG_API'] + '/schemas',)
        response.raise_for_status()
        schemas = response.json()
        return schemas
    except requests.exceptions.RequestException as e:
        print(f"Error fetching schemas: {e}")
        return None


    

class User(Resource):
    def get(self):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return {"error": "Authorization header missing"}, 401

        public_key = get_public_key()

        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != 'Bearer':
            return {"error": "Invalid Authorization header format"}, 401

        token = parts[1]

        try:
            payload = jwt.decode(token, public_key, algorithms=['RS256'])
            return payload, 200
        except ExpiredSignatureError:
            print('Expired token')
            return {"error": "Expired token"}, 401
        except InvalidTokenError:
            print('Invalid token')
            return {"error": "Invalid token"}, 401

       


class Projects(Resource):
    @swagger.doc({
        'tags': ['projects'],
        'description': 'Get all projects',
        'responses': {
            '200': {
                'description': 'List of projects'
            }
        }
    })
    def get(self):
        projects = Project.query.all()
        project_list = []
        for project in projects:
            project_data = {
                'id': project.id,
                'title': project.title,
                'pid': project.pid,
                'group': project.group,
                'description': project.description,
                'owner_id': project.owner_id,
                'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': project.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            project_list.append(project_data)
        return project_list
    
    @jwt_required()
    @swagger.doc({
        'tags': ['projects'],
        'description': 'Create a new project',
        'parameters': [
            {
                'name': 'title',
                'description': 'Project title',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'pid',
                'description': 'Project ID',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'pathogen_id',
                'description': 'Pathogen ID',
                'in': 'formData',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'group',
                'description': 'Project group',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'description',
                'description': 'Project description',
                'in': 'formData',
                'type': 'string',
                'required': False
            }
        ],
        'responses': {
            '201': {
                'description': 'Project created'
            }
        }
    })
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True)
        parser.add_argument('pid', required=True)
        parser.add_argument('pathogen_id', required=True)
        parser.add_argument('group', required=True)
        parser.add_argument('description', required=False)
        args = parser.parse_args()


        claims = get_jwt()
        if app.config['PROJECT_GROUP'] in claims['context']['user']['groups']:

            new_project = Project(
                title=args['title'],
                pid=args['pid'],
                pathogen_id=args['pathogen_id'],
                group=args['group'],
                description=args['description'],
                owner_id=get_jwt_identity()
            )

            db.session.add(new_project)
            db.session.commit()

            return new_project.as_dict(), 201
    
        else:
            return {'message': 'You do not have the required permissions to create a project'}, 401
        

    @jwt_required()
    @swagger.doc({
        'tags': ['projects'],
        'description': 'Update a project',
        'parameters': [
            {
                'name': 'id',
                'description': 'Project ID',
                'in': 'formData',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'title',
                'description': 'Project title',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'pid',
                'description': 'Project ID',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'pathogen_id',
                'description': 'Pathogen ID',
                'in': 'formData',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'group',
                'description': 'Project group',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'description',
                'description': 'Project description',
                'in': 'formData',
                'type': 'string',
                'required': False
            }
        ],
        'responses': {
            '200': {
                'description': 'Project updated'
            }
        }
    })
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('title')
        parser.add_argument('pid')
        parser.add_argument('pathogen_id')
        parser.add_argument('group')
        parser.add_argument('description')
        args = parser.parse_args()

        project = db.session.get(Project, args['id'])
        if not project:
            return {'message': 'Project not found'}, 404

        if args['title']:
            project.title = args['title']
        if args['pid']:
            project.pid = args['pid']
        if args['pathogen_id']:
            project.pathogen_id = args['pathogen_id']
        if args['group']:
            project.group = args['group']
        if args['description']:
            project.description = args['description']

        claims = get_jwt()
        if app.config['PROJECT_GROUP'] in claims['context']['user']['groups']:
            db.session.commit()
        else:
            return {'message': 'You do not have the required permissions to update this project'}, 401

        return project.as_dict(), 200
    
    @jwt_required()
    @swagger.doc({
        'tags': ['projects'],
        'description': 'Delete a project',
        'parameters': [
            {
                'name': 'id',
                'description': 'Project ID',
                'in': 'formData',
                'type': 'integer',
                'required': True
            }
        ],
        'responses': {
            '204': {
                'description': 'Project deleted'
            }
        }
    })
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()

        project = db.session.get(Project, args['id'])
        if not project:
            return {'message': 'Project not found'}, 404
        
        claims = get_jwt()
        if app.config['PROJECT_GROUP'] in claims['context']['user']['groups']:
            db.session.delete(project)
            db.session.commit()
            return {'message': 'Project deleted'}, 204
        else:
            return {'message': 'You do not have the required permissions to delete this project'}, 401

        
    
class Pathogens(Resource):

    @swagger.doc({
        'tags': ['pathogens'],
        'description': 'Get all pathogens',
        'responses': {
            '200': {
                'description': 'List of pathogens'
            }
        }
    })
    def get(self):
        pathogens = Pathogen.query.all()
        pathogen_list = []
        for pathogen in pathogens:
            pathogen_data = {
                'id': pathogen.id,
                'common_name': pathogen.common_name,
                'scientific_name': pathogen.scientific_name,
                'schema': pathogen.schema,
                'created_at': pathogen.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': pathogen.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            pathogen_list.append(pathogen_data)
        return pathogen_list
    

    @jwt_required()
    @swagger.doc({
        'tags': ['pathogens'],
        'description': 'Create a new pathogen',
        'parameters': [
            {
                'name': 'common_name',
                'description': 'Common name',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'scientific_name',
                'description': 'Scientific name',
                'in': 'formData',
                'type': 'string',
                'required': True
            },
            {
                'name': 'schema',
                'description': 'Pathogen schema',
                'in': 'formData',
                'type': 'string',
                'required': False
            }
        ],
        'responses': {
            '201': {
                'description': 'Pathogen created'
            }
        }
    })
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('common_name', required=True)
        parser.add_argument('scientific_name', required=True)
        parser.add_argument('schema')
        args = parser.parse_args()

        claims = get_jwt()
        if app.config['PATHOGEN_GROUP'] in claims['context']['user']['groups']:
            new_pathogen = Pathogen(
                common_name=args['common_name'],
                scientific_name=args['scientific_name'],
                schema=args['schema']
            )

            db.session.add(new_pathogen)
            db.session.commit()

            return new_pathogen.as_dict(), 201
        else:
            return {'message': 'You do not have the required permissions to create a pathogen'}, 401
    

    @jwt_required()
    @swagger.doc({
        'tags': ['pathogens'],
        'description': 'Update a pathogen',
        'parameters': [
            {
                'name': 'id',
                'description': 'Pathogen ID',
                'in': 'formData',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'common_name',
                'description': 'Common name',
                'in': 'formData',
                'type': 'string',
                'required': False
            },
            {
                'name': 'scientific_name',
                'description': 'Scientific name',
                'in': 'formData',
                'type': 'string',
                'required': False
            },
            {
                'name': 'schema',
                'description': 'Pathogen schema',
                'in': 'formData',
                'type': 'string',
                'required': False
            }
        ],
        'responses': {
            '200': {
                'description': 'Pathogen updated'
            }
        }
    })
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('common_name')
        parser.add_argument('scientific_name')
        parser.add_argument('schema')
        args = parser.parse_args()

        pathogen = db.session.get(Pathogen, args['id'])
        if not pathogen:
            return {'message': 'Pathogen not found'}, 404

        if args['common_name']:
            pathogen.common_name = args['common_name']
        if args['scientific_name']:
            pathogen.scientific_name = args['scientific_name']
        if args['schema']:
            pathogen.schema = args['schema']

        claims = get_jwt()
        if app.config['PATHOGEN_GROUP'] in claims['context']['user']['groups']:
            db.session.commit()
        else:
            return {'message': 'You do not have the required permissions to update this pathogen'}, 401

        return pathogen.as_dict(), 200
    
    @jwt_required()
    @swagger.doc({
        'tags': ['pathogens'],
        'description': 'Delete a pathogen',
        'parameters': [
            {
                'name': 'id',
                'description': 'Pathogen ID',
                'in': 'formData',
                'type': 'integer',
                'required': True
            }
        ],
        'responses': {
            '204': {
                'description': 'Pathogen deleted'
            }
        }
    })
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()

        pathogen = db.session.get(Pathogen, args['id'])
        if not pathogen:
            return {'message': 'Pathogen not found'}, 404
        
        claims = get_jwt()
        if app.config['PATHOGEN_GROUP'] in claims['context']['user']['groups']:
            db.session.delete(pathogen)
            db.session.commit()
            return {'message': 'Pathogen deleted'}, 204
        else:
            return {'message': 'You do not have the required permissions to delete this pathogen'}, 401


class Studies(Resource):

    @swagger.doc({
        'tags': ['studies'],
        'description': 'Get all studies',
        'responses': {
            '200': {
                'description': 'List of studies'
            }
        }
    })
    def get(self):
        pass
    
    def post(self):
        pass
    
    def put(self):
        pass
    
    def delete(self):
        pass


api.add_resource(User, '/api/')
api.add_resource(Projects, '/api/projects/')
api.add_resource(Pathogens, '/api/pathogens/')
api.add_resource(Studies, '/api/studies/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
