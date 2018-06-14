import glob

if __name__ == '__main__':
    test_files = glob.glob("tests/test_*.py")
    for test in test_files:
        print("*-*-*-*-*-* Testing file: "+test+"*-*-*-*-*-*")
        execfile(test)
