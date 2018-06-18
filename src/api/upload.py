def upload_video(video, title, bucket_name):
    """Uploads a given StringIO object to S3. Closes the file after upload.

    Returns the URL for the object uploaded.

    Note: The acl for the file is set as 'public-acl' for the file uploaded.

    Keyword Arguments:
    video -- video which needs to be uploaded.
    title -- video title.
    content_type -- content type that needs to be set for the S3 object.
    bucket_name -- name of the path where file needs to be uploaded.
    """
    pass
