from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful_swagger_2 import Api as SwaggerApi
from flask_cors import CORS
from config import Config
from models import db
import os

from Projects import Projects
from Pathogens import Pathogens
from Studies import Studies

from ego import get_public_key

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


### DUMMY ROUTE
# A dummy route to test various function

@app.route('/sandpit')
@jwt_required()
def sandpit():
    return 'play around here'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')