import unittest, json, os
import glob, mock
import random, string
from api import upload

# Helper function
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class YoutubeUpload(unittest.TestCase):

    def setUp(self):
        """*-*-*- Define test variables and initialize app."""
        # Mock external module
        # self.upload_patch = mock.patch("api.upload")
        # self.mock_upload = self.upload_patch.start()

    def tearDown(self):
        """*-*-*- Clean test variables."""
        # Stop upload module
        # self.mock_upload = self.upload_patch.stop()

    def test_video_upload_missing_argument(self):
        """*-*-*- Test API upload video missing arguments"""
        res = upload.youtube('','','')
        self.assertEqual('ok',res['status'])
        
    
suite = unittest.TestLoader().loadTestsFromTestCase(YoutubeUpload)
unittest.TextTestRunner(verbosity=2).run(suite)
