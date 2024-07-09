from flask import Flask, send_from_directory, jsonify, abort
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful_swagger_2 import Api as SwaggerApi
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from config import Config
from models import db
import os
import logging

from Projects import Projects
from Pathogens import Pathogens
from Studies import Studies

from ego import get_public_key, get_application_token, new_ego_group

from ego import user_has_permission, user_in_group


app = Flask(__name__)
app.config.from_object(Config)

### CORS

CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS, "methods": ["GET", "POST", "PUT", "DELETE"]}})

### DB

db.init_app(app)
migrate = Migrate(app, db)

### JWT

app.config['JWT_PUBLIC_KEY'] = get_public_key()

jwtm = JWTManager(app)

### SWAGGER DOCS

@app.route('/swagger.json')
def swagger_json():
    return send_from_directory(os.getcwd(), 'swagger.json')

SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)

app.register_blueprint(swaggerui_blueprint, url_prefix = SWAGGER_URL)

### API

api = SwaggerApi(app, api_version='0.1', api_spec_url=SWAGGER_URL)


### ROUTES

api.add_resource(Pathogens, 
    '/api/pathogens',
    '/api/pathogens/<string:id>'
)
api.add_resource(Projects, 
    '/api/projects',
    '/api/projects/<string:id>',
    '/api/projects/<string:id>/users/<string:user_id>'
)
api.add_resource(Studies, 
    '/api/studies',
    '/api/studies/<string:study_id>',
    '/api/studies/<string:study_id>/users/<string:user_id>',
    '/api/studies/<string:study_id>/users/<string:user_id>/<string:role>'
)

### ERROR HANDLERS
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(e)

    if isinstance(e, HTTPException):
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response
    else:
        return jsonify({
            "code": 500,
            "name": "Internal Server Error",
            "description": str(e),
        }), 500
    

### DUMMY ROUTE
# A dummy route to test various function

@app.route('/sandpit')
@jwt_required()
def sandpit():
    return {'message': 'Experimental endpoint'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')