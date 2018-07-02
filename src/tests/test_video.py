import unittest, json, os
import glob, mock
import random, string
from api import create_api

# Helper function
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class VideoRequests(unittest.TestCase):

    def setUp(self):
        """*-*-*- Define test variables and initialize app."""
        self.app = create_api("testing")
        self.client = self.app.test_client

        # binds the app to the current context
        ctx = self.app.app_context()
        ctx.push()

        # Mock upload module
        self.upload_patch = mock.patch("api.upload")
        self.mock_upload = self.upload_patch.start()

    def tearDown(self):
        """*-*-*- Clean test variables."""
        # Stop upload module
        self.mock_upload = self.upload_patch.stop()

    def checkApiResponse(self):
        return self.client().post('/api/video',data= dict(
            title='Test video',
            video= open("tests/videos/valid/mp4-sample.mp4", 'rb')
        ))

    def test_video_upload_missing_argument(self):
        """*-*-*- Test API upload video missing arguments"""
        res = self.client().post('/api/video')
        self.assertEqual(res.status_code, 400)
        self.assertEqual({'message':{'title':'Title argument is required.'}}, json.loads(res.data))
        
        res = self.client().post('/api/video',data= dict(
            title='Test video'
        ))
        self.assertEqual(res.status_code, 400)
        self.assertEqual({'message':{'video':'Video file is required.'}}, json.loads(res.data))
        
        res = self.client().post('/api/video',data= dict(
            title='',
            video= open("tests/videos/valid/mp4-sample.mp4", 'rb')
        ))
        self.assertEqual(res.status_code, 400)
        self.assertEqual({'error':'Title cannot be blank.'}, json.loads(res.data))
        
        
    def test_video_upload_invalid_extension(self):
        """*-*-*- Test API upload video invalid extension"""
        test_files = glob.glob("tests/videos/invalid/sample.*")
        for test in test_files:
            print(test)
            res = self.client().post('/api/video',data= dict(
                title='Test video',
                video= open(test, 'rb')
            ))
            self.assertEqual(res.status_code, 400)
            self.assertEqual({'error':'Video extension not supported.'}, json.loads(res.data))
        
    def test_video_upload_valid_extension(self):
        """*-*-*- Test API upload video valid extensions"""
        test_files = glob.glob("tests/videos/valid/*-sample.*")
        for test in test_files:
            upload_res = {'status':'ok','message': id_generator(size=12) }
            self.mock_upload.youtube.return_value = upload_res
            print(open(test, 'rb'))
            video = open(test, 'rb')
            res = self.client().post('/api/video',data= dict(
                title = 'Test video '+test,
                video = video))
            # ToDo: change ANY for the actual file call
            self.mock_upload.youtube.assert_called_with(mock.ANY,'Test video '+ test,'ipsy')
            self.assertEqual(upload_res['status'],json.loads(res.data)['status'])
            self.assertEqual(upload_res['message'],json.loads(res.data)['message'])

    
    def test_video_upload_error(self):
        """*-*-*- Test API call to upload video error"""
        upload_res = {'status':'fail','error': id_generator(size=12) }
        self.mock_upload.youtube.return_value = upload_res
        res = self.checkApiResponse()
        self.assertEqual(res.status_code, 500)
        self.assertEqual(upload_res, json.loads(res.data))
        
    def test_video_propagate_exceptions(self):
        """*-*-*- Test to propagate exceptions"""
        self.mock_upload.youtube.side_effect = Exception
        with self.assertRaises(Exception):
            res = json.loads(self.checkApiResponse())
        
    
suite = unittest.TestLoader().loadTestsFromTestCase(VideoRequests)
unittest.TextTestRunner(verbosity=2).run(suite)
