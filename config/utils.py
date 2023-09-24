import os
import threading
import datetime
import base64

MAIN_SCRIPT_DIR = None

def set_main_script_dir(dir_path):
    global MAIN_SCRIPT_DIR
    MAIN_SCRIPT_DIR = dir_path

def get_main_script_dir():
    return MAIN_SCRIPT_DIR

# convert image to blob data
def convert_to_blod_data(filename):
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

# write 
def write_to_file(data, dirPath):

    # remove files in directory
    remove_files_in_directory(dirPath)

    filename = dirPath + '\\' + str(int(datetime.datetime.now().timestamp())) + '.mp4'
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")
    return filename


def remove_files_in_directory(directory):
    # Iterate over all the files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # Check if the current iteration is a file
        try:
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except:
            print('delete_file_error_continue-----------')
            continue



FILELOCK_LOCK = 0
fileLockList = []
def initFileLock():
    global fileLockList
    fileLockList.append(threading.Lock())

def getFileLock(file):
    return fileLockList[file]


THREAD_INIT = 0
THREAD_RUNNING = 1
THREAD_STOPPING = 2
THREAD_FINISHED = 3

threadStatus = []
def initThreadLock():
    global threadStatus
    threadStatus.append(THREAD_INIT)

def setThreadStatus(status):
    global threadStatus
    threadStatus[0] = status

def getThreadStatus():
    global threadStatus
    return threadStatus[0]