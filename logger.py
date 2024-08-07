import os
import time
import getpass
import csv
from pymediainfo import MediaInfo

# Code from IFIScripts github repository
def make_desktop_logs_dir():
    desktop_logs_dir = os.path.expanduser("~/Desktop/ucclibrary_logs")
    os.makedirs(desktop_logs_dir, exist_ok= True)
    return desktop_logs_dir

def generate_log(log, what2log):
    if not os.path.isfile(log):
        with open(log, "w", encoding='utf-8') as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ")
                     + getpass.getuser()
                     + ' ' + what2log + ' \n')
    else:
        with open(log, "a", encoding='utf-8') as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ")
                     + getpass.getuser()
                     + ' ' + what2log + ' \n')

def remove_bad_files(root_dir, log_name_source):
    '''
    Removes unwanted files.
    Verify if this is different than the same function in ififuncs.
    '''
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, _, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print(('***********************' + 'removing: ' + path))
                    generate_log(
                        log_name_source,
                        'EVENT = Unwanted file removal - %s was removed' % path
                    )
                    try:
                        os.remove(path)
                    except OSError:
                        print('can\'t delete as source is read-only')