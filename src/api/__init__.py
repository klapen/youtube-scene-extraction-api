from flask import Flask
from flask_restful import Resource, Api
from instance.config import app_config

def create_api(config_name):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    api = Api(app)

    class Hello(Resource):
        def get(self):
            return {'status': 'ok'}

    api.add_resource(Hello, '/api')

    return app
