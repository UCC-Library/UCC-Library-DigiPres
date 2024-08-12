#!/usr/bin/env python3
import os
import argparse
import time
import sys
from logger import make_desktop_logs_dir, generate_log, remove_bad_files

def arg_parse():

    '''
    Enter the arguments required 
    '''

    parser = argparse.ArgumentParser(
        description="Generates the synopsis of folder contents"
    )

    parser.add_argument('-i', 
                        required=True,
                        type=str, 
                        help="Full path of input directory to summarize")

    parser.add_argument('-formats',
                        required=True,
                        type=str,
                        default="",
                        help="Enter the file formats to be removed from the directory structure")

    parser.add_argument('-refs',
                        choices=['y','n'],
                        type=str,
                        default='n',
                        help="full path of output directory")     

    parsed_args = parser.parse_args()
    return parsed_args

def main():

    args = arg_parse()
    input_path = args.i
    log_name_source_ = "remove_bad_"  + str(os.path.basename(input_path)) + time.strftime("_%Y_%m_%dT%H_%M_%S") + ".log"
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source = os.path.join(desktop_logs_dir, log_name_source_)

    if not os.path.isdir(input_path):
        print(' - Input must be a directory/folder - exiting!')
        generate_log(log_name_source, ' - Input must be a directory/folder - exiting!')
        sys.exit()
    
    remove_bad_files(input_path, log_name_source)

    formats = list(str(args.formats).strip().split(' '))
    for root, subdirs, files in os.walk(input_path):
        try:
            
            if files == () or files == []:
                continue

            for file in files:
                if str(os.path.splitext(file)[1]).lower() in formats:
                    print(f"File {file} removed from {root}")
                    generate_log(log_name_source, f"File {file} removed from {root}")
                    os.remove(os.path.join(root,file))
            
            
            if args.refs == 'y':
                for subdir in subdirs:
                    l = len(os.listdir(os.path.join(root,subdir)))
                    if l == 0:
                        print(f"Empty Folder {subdir} removed from {root}")
                        generate_log(log_name_source, f"Empty Folder {subdir} removed from {root}")
                        os.rmdir(os.path.join(root,subdir))
        
        except:
            continue

if __name__ == "__main__":
    main()
                
        
