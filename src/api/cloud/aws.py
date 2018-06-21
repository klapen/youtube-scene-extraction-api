import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

class S3AwsUploader():

    def __init__(self):
        self.__config = Config(region_name='us-east-2',
                             retries={'max_attempts': 15},
                             max_pool_connections=20,
                             s3={'use_accelerate_endpoint':True,
                                 'path':'ipsy.s3-accelerate.amazonaws.com'})
        self.client = boto3.client('s3',config=self.__config)
        
    def __checkFolderString__(self,folder_name):
        if(not folder_name.endswith('/')):
            folder_name = folder_name+'/'
        return folder_name
        
    def objectExist(self, bucket_name, key):
        try:
            self.client.head_object(Bucket=bucket_name, Key=key)
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True
    
    def createFolder(self,name,bucket_name):
        name = self.__checkFolderString__(name)
        if(self.objectExist(bucket_name, name)):
            return True
        else: 
            res = self.client.put_object(Bucket=bucket_name,Body='',Key=name)
            return 'ResponseMetadata' in res and res['ResponseMetadata']['HTTPStatusCode'] == 200
        
    def s3UploadFile(self,ufile,user_folder,bucket):
        user_folder = self.__checkFolderString__(user_folder)
        if(self.createFolder(user_folder,bucket)):
            filename = ufile.filename.split('/')[-1]
            folder_name = filename.replace('.','-')+'/'
            if(self.createFolder(user_folder+folder_name,bucket)):
                # res = self.client.upload_fileobj(ufile, bucket, user_folder +folder_name + filename)
                # return 'ResponseMetadata' in res and res['ResponseMetadata']['HTTPStatusCode'] == 200
                return True
            else:
                return False
        else:
            return False
