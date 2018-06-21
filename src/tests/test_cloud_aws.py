import unittest, mock, copy
import boto3
from api.cloud.aws import S3AwsUploader
from botocore.stub import Stubber

from botocore.exceptions import ClientError

# Mock FileStorage
from werkzeug.test import EnvironBuilder

class AwsCloudUpload(unittest.TestCase):

    def setUp(self):
        """*-*-*- Define test variables and initialize app."""
        # Mock external module
        self.uploader = S3AwsUploader()
        self.client = self.uploader.client
        self.stubber = Stubber(self.client)
        self.stubber.activate()

    def tearDown(self):
        """*-*-*- Clean test variables."""
        # Stop modules
        self.stubber.deactivate()

    def test_cloud_client_config(self):
        """ *-*-*- Test client configuration """
        self.assertEqual('us-east-2', self.client._client_config.region_name)
        self.assertEqual({'max_attempts': 15}, self.client._client_config.retries)
        self.assertEqual(20, self.client._client_config.max_pool_connections)
        self.assertEqual({'use_accelerate_endpoint':True,'path':'ipsy.s3-accelerate.amazonaws.com'}, self.client._client_config.s3)

    def test_cloud_upload_new_user_file(self):
        """*-*-*- Test cloud module to upload file to S3 for a new file without a folder."""
        user_folder = 'user-test/'
        filename = 'avi-sample.avi'
        file_folder = filename.replace('.','-')+'/'
        with open('tests/videos/valid/'+filename,'rb') as fb:
                builder = EnvironBuilder(method='POST', data={'file': (fb, filename)})
                ufile = builder.files.popitem()[1]
                mock_file = copy.deepcopy(ufile)

                # Set client mock responses
                self.stubber.add_client_error('head_object',http_status_code=404,
                                              service_error_code='404')
                self.stubber.add_response('put_object',
                                          {'ResponseMetadata':{'HTTPStatusCode':200}},
                                          expected_params={'Bucket':'ipsy','Body':'','Key':user_folder})
                self.stubber.add_client_error('head_object',http_status_code=400,
                                              service_error_code='404')
                self.stubber.add_response('put_object',
                                          {'ResponseMetadata':{'HTTPStatusCode':200}},
                                          expected_params={'Bucket':'ipsy','Body':'','Key':user_folder+file_folder})
                # self.stubber.add_response('upload_fileobj',
                #                           {'ResponseMetadata':{'HTTPStatusCode':200}},
                #                           expected_params={'Fileobj':mock_file,
                #                                            'Bucket':'ipsy',
                #                                            'Key':user_folder+file_folder+filename})

                # Feature test
                self.assertTrue(self.uploader.s3UploadFile(ufile,user_folder,'ipsy'))
    
suite = unittest.TestLoader().loadTestsFromTestCase(AwsCloudUpload)
unittest.TextTestRunner(verbosity=2).run(suite)
