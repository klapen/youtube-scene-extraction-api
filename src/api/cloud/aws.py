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

    def getObjects(self,bucket_name,key):
        bucket = boto3.resource('s3').Bucket(bucket_name)
        return list(bucket.objects.filter(Prefix=key))

    def folderExist(self,bucket_name, folder_name):
        return len(self.getObjects(bucket_name,folder_name)) > 0
        
    def objectExist(self, bucket_name, key):
        return len(self.getObjects(bucket_name,key)) == 1
    
    def createFolder(self,name,bucket_name):
        name = self.__checkFolderString__(name)
        if(self.objectExist(bucket_name, name)):
            return True
        else: 
            res = self.client.put_object(Bucket=bucket_name,Body='',Key=name)
            return 'ResponseMetadata' in res and res['ResponseMetadata']['HTTPStatusCode'] == 200

    def bucketExist(self,bucket_name):
        s3 = boto3.resource('s3')
        return s3.Bucket(bucket_name) in s3.buckets.all()
        
    def uploadFile(self,ufile,user_folder,bucket_name):
        if(self.bucketExist(bucket_name)):
            user_folder = self.__checkFolderString__(user_folder)
            filename = ufile.filename.split('/')[-1]
            folder_name = filename.replace('.','-')+'/'
            # Upload de file
            self.client.upload_fileobj(ufile, bucket_name, user_folder +folder_name + filename)
            # Check it was created, because upload_fileobj returns None
            return self.objectExist(bucket_name, user_folder +folder_name + filename)
        else:
            return False
