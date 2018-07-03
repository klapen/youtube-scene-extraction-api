import os, glob
from cloud import aws
from werkzeug.datastructures import FileStorage
import pyscenedetector as psd

def send_video(video, title, bucket_name, username, scene_detection_mode = 'content'):
    """Uploads a given object to S3. Closes the file after upload.

    Returns the URL for the object uploaded.

    Note: The acl for the file is set as 'public-acl' for the file uploaded.

    Keyword Arguments:
    video -- video which needs to be uploaded.
    title -- video title.
    bucket_name -- name of the path where file needs to be uploaded.
    """
    if not title:
        return {'status':'error','message':'Title argument is required'}
    if not bucket_name:
        return {'status':'error','message':'Bucket name argument is required'}
    if not username:
        return {'status':'error','message':'Username argument is required'}
    if not video:
        return {'status':'error','message':'Video file is required'}

    # Check the file is FileStorage
    if not isinstance(video,FileStorage):
        return {'status':'error','message':'Video file is not a werkzeug.datastructures.FileStorage'}
    # Save file to temporal folder
    tmp_folder = reduce(os.path.join,[os.getenv('APP_TEMP_FOLDER'),username,video.filename.split('.')[:-1][0]])
    try:
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)
        video.save(os.path.join(tmp_folder,video.filename))
    except IOError as e:
        return {'status':'error','message':'Unable to write on temporary folder'}

    try:
        psd.video_detection(os.path.join(tmp_folder,video.filename),scene_detection_mode, username)
    except:
        return {'status':'error','message':'Error on scene detector module'}

    # ToDo: Add metadata on upload files
    aws_uploader = aws.S3AwsUploader()
    if aws_uploader.uploadVideoFile(video,username,bucket_name):
        fail_upload_files = []
        folder_name = video.filename.replace('.','-')+'/'
        for f in glob.glob(os.path.join(tmp_folder,video.filename+"*.jpg")):
            if not aws_uploader.uploadFile(f,folder_name,username,bucket_name):
                fail_upload_files.append(f)
        if fail_upload_files:
            return {'status':'error','message':'Error uploading scene files', 'not_uploaded':fail_upload_files}
        else:
            return {'status':'ok'}
    else:
        return {'status':'error','message':'Error uploading video'}
