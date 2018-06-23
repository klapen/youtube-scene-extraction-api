import unittest, mock, copy, glob
import boto3
from api.cloud.aws import S3AwsUploader
from botocore.stub import Stubber

from botocore.exceptions import ClientError

# Mock FileStorage
from werkzeug.test import EnvironBuilder

# Helper function
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# ToDo: Change to unit test using a boto3 mock
class AwsCloudUpload(unittest.TestCase):
    """ This is a functional test"""
    @classmethod
    def setUpClass(cls):
        cls._test_bucket_name = 'ipsy'
        cls._user_folder = 'user-test/'

    def upload_test_file(self,filename,callback):
        file_folder = filename.replace('.','-')+'/'
        with open('tests/videos/valid/'+filename,'rb') as fb:
            builder = EnvironBuilder(method='POST', data={'file': (fb, filename)})
            ufile = builder.files.popitem()[1]
            mock_file = copy.deepcopy(ufile)
            
            # execute the callback
            callback(ufile, file_folder, filename);
            
    def setUp(self):
        """*-*-*- Define test variables and initialize app."""
        # Mock external module
        self.uploader = S3AwsUploader()
        self.client = self.uploader.client
        self.delete_files = False

    def tearDown(self):
        """*-*-*- Clean test variables."""
        # Delete created files
        if(self.delete_files):
            print("Delete files")
            aws_bucket = boto3.resource('s3').Bucket(self._test_bucket_name)
            aws_bucket.objects.filter(Prefix="user-test").delete()

    def test_cloud_client_config(self):
        """ *-*-*- Test client configuration """
        self.assertEqual('us-east-2', self.client._client_config.region_name)
        self.assertEqual({'max_attempts': 15}, self.client._client_config.retries)
        self.assertEqual(20, self.client._client_config.max_pool_connections)
        self.assertEqual({'use_accelerate_endpoint':True,'path':'ipsy.s3-accelerate.amazonaws.com'}, self.client._client_config.s3)

        
    def bucket_exists(self, ufile, file_folder, filename):
        """ Callback function to test try upload file on non existing bucket """
        # Feature test
        self.assertFalse(self.uploader.uploadFile(ufile,self._user_folder,self._test_bucket_name+'2'))
        self.assertFalse(self.uploader.folderExist(self._test_bucket_name,self._user_folder))
        self.assertFalse(self.uploader.folderExist(self._test_bucket_name,self._user_folder+file_folder))
        self.assertFalse(self.uploader.objectExist(self._test_bucket_name,self._user_folder+file_folder+filename))
        
    def test_cloud_bucket_exists(self):
        """*-*-*- Test try upload file on non existing bucket *-*-*-"""
        self.assertTrue(self.uploader.bucketExist(self._test_bucket_name))
        self.assertFalse(self.uploader.bucketExist(self._test_bucket_name+'2'))

        # Upload file on no created bucket
        self.upload_test_file('avi-sample.avi',self.bucket_exists)

    def new_user_file(self, ufile, file_folder, filename):
        """ Callback function for test upload file creating required folders """
        self.assertTrue(self.uploader.uploadFile(ufile,self._user_folder,self._test_bucket_name))
        self.assertTrue(self.uploader.folderExist(self._test_bucket_name,self._user_folder))
        self.assertTrue(self.uploader.folderExist(self._test_bucket_name,self._user_folder+file_folder))
        self.assertTrue(self.uploader.objectExist(self._test_bucket_name,self._user_folder+file_folder+filename))

        self.delete_files = True

    def test_cloud_upload_new_user_file(self):
        """*-*-*- Test cloud module to upload file to S3 creating required folders."""
        self.upload_test_file('avi-sample.avi', self.new_user_file)
           
suite = unittest.TestLoader().loadTestsFromTestCase(AwsCloudUpload)
unittest.TextTestRunner(verbosity=2).run(suite)
