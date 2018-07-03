import unittest, json, os, copy, shutil
import glob, mock
import random, string, datetime
from api import upload

# Mock FileStorage
from werkzeug.test import EnvironBuilder
from werkzeug.datastructures import FileStorage

# Helper function
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class VideoUpload(unittest.TestCase):

    def setUp(self):
        """*-*-*- Define test variables and initialize app."""
        # Mock external module
        self.aws_patch = mock.patch("api.cloud.aws")
        self.mock_aws = self.aws_patch.start()
        self.psd_patch = mock.patch("api.pyscenedetector")
        self.mock_psd = self.psd_patch.start()
        self.delete_files = False
        
    def tearDown(self):
        """*-*-*- Clean test variables."""
        # Stop upload module
        self.mock_aws = self.aws_patch.stop()
        self.mock_psd = self.psd_patch.stop()
        if self.delete_files:
            shutil.rmtree(os.getenv('APP_TEMP_FOLDER'))
            

    def test_video_upload_missing_argument(self):
        """*-*-*- Test API upload video missing arguments"""
        res = upload.send_video('','','','')
        self.assertEqual('error',res['status'])
        self.assertEqual('Title argument is required',res['message'])

        res = upload.send_video('','Title test','','')
        self.assertEqual('error',res['status'])
        self.assertEqual('Bucket name argument is required',res['message'])

        res = upload.send_video('','Title test','testbucket','')
        self.assertEqual('error',res['status'])
        self.assertEqual('Username argument is required',res['message'])

        res = upload.send_video('','Title test','testbucket','user-test')
        self.assertEqual('error',res['status'])
        self.assertEqual('Video file is required',res['message'])
            
    def test_video_file_not_type(self):
        filename = 'avi-sample.avi'
        with open('tests/videos/valid/'+filename,'rb') as fb:
            res = upload.send_video(fb,'Title test','testbucket','user-test')
            self.assertEqual('error',res['status'])
            self.assertEqual('Video file is not a werkzeug.datastructures.FileStorage',res['message'])

            builder = EnvironBuilder(method='POST', data={'file': (fb, filename)})
            ufile = builder.files.popitem()[1]
            res = upload.send_video(ufile,'Title test','testbucket','user-test')
            self.assertEqual('ok',res['status'])

        self.delete_files = True
            
    def test_video_unable_to_write(self):
        with mock.patch('os.makedirs') as omd:
            omd.side_effect = IOError
            filename = 'avi-sample.avi'
            with open('tests/videos/valid/'+filename,'rb') as fb:
                builder = EnvironBuilder(method='POST', data={'file': (fb, filename)})
                ufile = builder.files.popitem()[1]
                res = upload.send_video(ufile,'Title test','testbucket','user-test')
                self.assertEqual('error',res['status'])
                self.assertEqual('Unable to write on temporary folder',res['message'])

    def test_video_propagate_exceptions(self):
        with mock.patch('os.makedirs') as omd:
            omd.side_effect = Exception
            with self.assertRaises(Exception):
                filename = 'avi-sample.avi'
                with open('tests/videos/valid/'+filename,'rb') as fb:
                    builder = EnvironBuilder(method='POST', data={'file': (fb, filename)})
                    ufile = builder.files.popitem()[1]
                    res = upload.send_video(ufile,'Title test','testbucket','user-test')

    @unittest.skip("ToDO: Mock FileStorage call to save")
    def test_video_save_temp_folder(self):
        pass

    @unittest.skip("ToDo: Not calling pyscenedetector mock")
    def test_video_extract_scenes(self):
        rnd_num = random.randint(3,15)
        psd_response = {
            'scenes_time': [str(datetime.timedelta(seconds=random.randint(120,444))) for _ in range(rnd_num) ],
            'scenes_file': ['file-'+str(x) for x in range(rnd_num)]
        }
        self.mock_psd.send_video.return_value = psd_response
        filename = 'avi-sample.avi'
        tmp_folder = reduce(os.path.join,[os.getenv('APP_TEMP_FOLDER'),
                                          'user-test',filename.split('.')[:-1][0]])
        with open('tests/videos/valid/'+filename,'rb') as fb:
            builder = EnvironBuilder(method='POST', data={'file': (fb, filename)})
            ufile = builder.files.popitem()[1]
            res = upload.send_video(ufile,'Title test','testbucket','user-test')

            print res
            self.mock_psd.video_detection.assert_called_with(os.path.join(tmp_folder,filename),
                                                             'content', 'user-test')
            self.assertEqual('ok',res['status'])
            
            
        self.delete_files = False
        
                    
suite = unittest.TestLoader().loadTestsFromTestCase(VideoUpload)
unittest.TextTestRunner(verbosity=2).run(suite)

