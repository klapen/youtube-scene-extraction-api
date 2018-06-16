import glob,os

if __name__ == '__main__':
    os.system('rm -f *-output.txt')
    video_files = glob.glob("valid/*-sample.*")
    for fvideo in video_files:
        print("*-*-*-*-*-* Extract PyDetectScene info: "+fvideo+"*-*-*-*-*-*")
        ext = fvideo.split('.')[1]
        os.system("scenedetect -d content -t 30 -i {0} > {1}-content-output.txt".format(fvideo,ext))
        os.system("scenedetect -d threshold -t 30 -i {0} > {1}-threshold-output.txt".format(fvideo,ext))
