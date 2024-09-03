#!/usr/bin/env python3
import os
import shutil
import argparse
import sys
import time
from logger import make_desktop_logs_dir, generate_log, remove_bad_files

def arg_parse():

    '''
    Enter the arguments required 
    '''

    parser = argparse.ArgumentParser(
        description="Generates the synopsis of folder contents. \
            Written by Abhijeet Rao, UCC 2023-2024."
    )

    parser.add_argument('-i', 
                        required=True,
                        type=str, 
                        help="Full path of input directory to summarize")

    # parser.add_argument('-o',
    #                     type=str,
    #                     default="",
    #                     help="full path of output directory")   

    parsed_args = parser.parse_args()
    return parsed_args

def main():
    
    args = arg_parse()
    input_path = args.i
    log_name_source_ = "folder_summary_"  + str(os.path.basename(input_path)) + time.strftime("_%Y_%m_%dT%H_%M_%S") + ".log"
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source = os.path.join(desktop_logs_dir, log_name_source_)
    # if args.o == "":
    #     output_file = os.path.join(os.path.dirname(input_path), os.path.basename(input_path) + ".txt")
    # else:
    #     output_file = os.path.join(args.o, os.path.basename(input_path) + '.txt')

    if not os.path.isdir(input_path):
        print(' - Input must be a directory/folder - exiting!')
        generate_log(log_name_source, ' - Input must be a directory/folder - exiting!')
        sys.exit()

    tracker = {}
    file_sizes = {}
    folder_counts = 0
    
    remove_bad_files(input_path, log_name_source)

    for root, subdirs, files in os.walk(input_path):

        folder_counts += len(subdirs)

        if files == () or files == []:
            continue

        for file in files:
            ext = str(os.path.splitext(file)[1]).lower()

            if ext == "":
                ext = "unknown"
            
            tracker[ext] = tracker.get(ext, 0) + 1
            
            size = (os.path.getsize(os.path.join(root, file)))
            
            file_sizes[ext + '_size'] = file_sizes.get(ext + '_size', 0) + size
            
    
    # print(output_file)
    
    
    print("*"*100 + "\n")
    print("Timestamp - " + time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")
    print(f"Directory details of - {input_path}".center(100) + "\n")
    generate_log(log_name_source, f"Directory details of - {input_path}".center(100) + "\n")
    print(f"Subdirectories count - {folder_counts}" + "\n")
    generate_log(log_name_source, f"Subdirectories count - {folder_counts}" + "\n")
    print("File-type".center(33) 
        +  "File-Counts".center(33) 
        + "Total-Size".center(33) + "\n")
    generate_log(log_name_source, "File-type".center(33) 
        +  "File-Counts".center(33) 
        + "Total-Size".center(33) + "\n")
    for file_type in tracker:
        print(str(file_type).center(33) 
            + str(tracker[file_type]).center(33) 
            + (str((file_sizes[file_type + '_size']) / (1024*1024)) + " MB").center(33)
            + "\n")
        generate_log(log_name_source, str(file_type).center(33) 
            + str(tracker[file_type]).center(33) 
            + (str((file_sizes[file_type + '_size'])/ (1024*1024)) + " MB").center(33)
            + "\n")

if __name__ == "__main__":
    main()