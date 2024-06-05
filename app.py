from json import JSONEncoder
from flask import Flask, request, jsonify
from flask_restful import Api as RestfulApi, Resource, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful_swagger_2 import Api as SwaggerApi, swagger
from flask_cors import CORS
from config import Config
from models import db, Project
import jwt
import datetime

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"]}})

# Ensure json_encoder is defined
if not hasattr(app, 'json_encoder'):
    app.json_encoder = JSONEncoder


# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwtm = JWTManager(app)
api = SwaggerApi(app, api_version='0.1', api_spec_url='/swagger')

# Swagger configuration
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

class User(Resource):
    @jwt_required()
    @swagger.doc({
        'tags': ['User'],
        'description': 'Returns user info from JWT token',
        'responses': {
            '200': {
                'description': 'JWT Payload',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': ''
                        }
                    }
                }
            }
        }
    })
    def get(self):
        claims = get_jwt() 
        return claims
    
class Projects(Resource):
    @swagger.doc({
        'tags': ['Projects'],
        'description': 'Get all projects from the database',
        'responses': {
            '200': {
                'description': 'List of projects',
                'schema': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/Project'
                    }
                }
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
                'description': project.description,
                'owner_id': project.owner_id,
                'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': project.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            project_list.append(project_data)
        return project_list
    
    # POST method (create new project)
    @swagger.doc({
        'tags': ['Projects'],
        'description': 'Create a new project',
        'parameters': [
            {
                'name': 'project',
                'description': 'Project details',
                'in': 'body',
                'schema': {
                    '$ref': '#/definitions/Project'
                }
            }
        ],
        'responses': {
            '201': {
                'description': 'Project created',
                'schema': {
                    '$ref': '#/definitions/Project'
                }
            }
        }
    })

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True)
        parser.add_argument('pid', required=True)
        parser.add_argument('description', required=True)
        args = parser.parse_args()

       
        new_project = Project(
            title=args['title'],
            pid=args['pid'],
            description=args['description'],
            owner_id=get_jwt_identity()
        )

        db.session.add(new_project)
        db.session.commit()

        return new_project.as_dict(), 201

    # PUT method (update an existing project)
    @swagger.doc({
        'tags': ['Projects'],
        'description': 'Update an existing project',
        'parameters': [
            {
                'name': 'id',
                'description': 'Project ID',
                'in': 'path',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'project',
                'description': 'Project details',
                'in': 'body',
                'schema': {
                    '$ref': '#/definitions/Project'
                }
            }
        ],
        'responses': {
            '200': {
                'description': 'Project updated',
                'schema': {
                    '$ref': '#/definitions/Project'
                }
            }
        }
    })
    
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('title')
        parser.add_argument('pid')
        parser.add_argument('description')
        args = parser.parse_args()

        project = Project.query.get(args['id'])
        if not project:
            return {'message': 'Project not found'}, 404

        if args['title']:
            project.title = args['title']
        if args['pid']:
            project.pid = args['pid']
        if args['description']:
            project.description = args['description']

        db.session.commit()

        return project.as_dict(), 200
    
    @swagger.doc({
        'tags': ['Projects'],
        'description': 'Delete an existing project',
        'parameters': [
            {
                'name': 'id',
                'description': 'Project ID',
                'in': 'path',
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

        project = Project.query.get(args['id'])
        if not project:
            return {'message': 'Project not found'}, 404

        db.session.delete(project)
        db.session.commit()

        return {}, 204
    
class GenerateToken(Resource):
    def get(self):
        user_payload = {
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "sub": "3423616",
            "iss": "ego",
            "jti": "2323232323",
            "context": {
                "scope": [
                    "VIRUS-SEQ.WRITE",
                    "VIRUS-SEQ.READ"
                ],
                "user": {
                    "email": "user@domain.com",
                    "status": "APPROVED",
                    "firstName": "Di",
                    "lastName": "MMM",
                    "createdAt": 1715867872506,
                    "lastLogin": 1717576566031,
                    "preferredLanguage": None,
                    "providerType": "KEYCLOAK",
                    "providerSubjectId": "eee",
                    "type": "ADMIN",
                    "groups": [
                        "1111"
                    ]
                }
            },
            "aud": []
        }
        
        # Create a token
        token = jwt.encode(user_payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})


# Add your routes
api.add_resource(User, '/api/')
api.add_resource(Projects, '/api/projects/')
api.add_resource(GenerateToken, '/api/generate-token')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
