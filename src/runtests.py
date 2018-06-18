import glob,sys,getopt

if __name__ == '__main__':
    argv = sys.argv[1:]
    try:
        opts,args = getopt.getopt(argv, "ht:",["test-file="])
    except getopt.GetopError:
        print 'runtest.py -t [path/to/file/test.py]'
        sys.exit(2)
        
    for opt,arg in opts:
        if opt == '-h':
            print """
            usage: python runtest.py [options]
            
            If there is no option, it will run all files on tests/ folder that match the filename test_*.py

            Options and arguments:
            -t --test-file  : Save images for scene detection.
            """
            sys.exit()
        elif opt in ("-t","--test-file"):
            print("*-*-*-*-*-* Testing file: "+arg+"*-*-*-*-*-*")
            execfile(arg)
            sys.exit()

    # If no option, run all tests
    test_files = glob.glob("tests/test_*.py")
    for test in test_files:
        print("*-*-*-*-*-* Testing file: "+test+"*-*-*-*-*-*")
        execfile(test)
