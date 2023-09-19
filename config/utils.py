import os
# dbPath = './DbFuncs/sql.db'

# screenX = 600
# screenY = 900

# itemLength = 220

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
def write_to_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")


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