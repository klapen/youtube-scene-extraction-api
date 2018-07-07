import os, glob
import scenedetect

def video_detection(filepath,detector,username,save_images = True):
    """Performs scene detection on passed file using given scene detector.

    args:
        filepath:    A string containing the path/to/file/filename.
        detector:    Scene detection mode, with only 2 options: content or threshold
        username:    Username calling the fuction, to organize outputfiles
    kwargs:
        save_images: Boolean to save images on disk 
    
    Returns:
        Dictionary with 2 fields
             scenes_time:  Array with scene boundaries in timecode strings ("HH:MM:SS.nnn")
             scene_files:  Array with scene files path. Empty id save_images is False
    """
    
    scene_list = [] # Scenes will be added to this list in detect_scenes().

    # Usually use one detector, but multiple can be used.
    # By default it is content detector
    detector = detector.lower()
    if(detector == 'threshold'):
        detector_list = [scenedetect.detectors.ThresholdDetector(threshold = 16, min_percent = 0.9)]
    else:
        detector_list = [scenedetect.detectors.ContentDetector(threshold = 30, min_scene_len = 15)]
        
    video_fps, frames_read = scenedetect.detect_scenes_file(filepath, scene_list, detector_list, save_images = save_images, quiet_mode=True)

    # Organize frames
    path, filename = os.path.split(filepath)
    scene_files = glob.glob(filename+'.Scene*-OUT.jpg')
    output_path = reduce(os.path.join,[os.getenv('APP_TEMP_FOLDER'),username,filename.split('.')[:-1][0]])
    output_lambda = lambda x : os.path.join(output_path,x.replace('-OUT',''))
    if save_images:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Preserve only OUT scene files to bind with time
        [os.rename(x,output_lambda(x)) for x in scene_files]

        # Remove all other files
        [os.remove(x) for x in glob.glob(filename+'.Scene*-IN.jpg')]

    # create new list with scene boundaries in milliseconds instead of frame #.
    scene_list_msec = [(1000.0 * x) / float(video_fps) for x in scene_list]
    # create new list with scene boundaries in timecode strings ("HH:MM:SS.nnn").
    scene_list_tc = [scenedetect.timecodes.get_string(x) for x in scene_list_msec]
    return {'scenes_time': scene_list_tc,
            'scenes_file': [output_lambda(x) for x in scene_files] if scene_files else [] }
