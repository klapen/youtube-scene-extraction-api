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
            return {'status': 'ok'}, 200

    class VideoList(Resource):
        # Retrieve a list of videos
        def get(self):
            pass

    class Video(Resource):
        # Retieve a single video information
        def get(self):
            pass

        # Add a video
        def post(self):
            pass

        # Delete a given video ID
        def delete(self):
            pass

    api.add_resource(Hello, '/api')
    api.add_resource(VideoList, '/api/video')
    api.add_resource(Video, '/api/video/<int:id>')

    return app
