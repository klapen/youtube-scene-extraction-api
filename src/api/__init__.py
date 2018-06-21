from flask import Flask
from flask_restful import Resource, Api, reqparse
from werkzeug.datastructures import FileStorage
from instance.config import app_config
import upload

ALLOWED_EXTENSIONS = set(['3gp', 'avi', 'flv', 'mkv', 'mov', 'mp4','mpg','wmv'])
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_api(config_name):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    api = Api(app)

    class Hello(Resource):
        def get(self):
            return {'status': 'ok'}, 200

    class VideoList(Resource):
        
        # Retrieve a list of videos
        def get(self):
            pass
    
        # Add a video
        def post(self):
            parse = reqparse.RequestParser()
            parse.add_argument('title', required=True, help="Title argument is required.")
            parse.add_argument('video', required=True, help="Video file is required.",
                               type=FileStorage, location='files')

            args = parse.parse_args()
            
            if args['title'] == '':
                return {'error': 'Title cannot be blank.'}, 400
            if not allowed_file(args['video'].filename):
                return {'error': 'Video extension not supported.'}, 400

            res = upload.youtube(args['video'],args['title'],'ipsy')
            return res, 500 if(res['status'] != 'ok') else 200

    class Video(Resource):
        # Retieve a single video information
        def get(self):
            pass

        # Delete a given video ID
        def delete(self):
            pass

    api.add_resource(Hello, '/api')
    api.add_resource(VideoList, '/api/video')
    api.add_resource(Video, '/api/video/<int:id>')

    return app

