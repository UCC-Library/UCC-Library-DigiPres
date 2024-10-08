#!/usr/bin/env python3
import os
import argparse
import time
import sys
from logger import make_desktop_logs_dir, generate_log, remove_bad_files

# Below function parses input arguments from the command line provided by the user.
def arg_parse():

    '''
    Enter the arguments required 
    '''

    parser = argparse.ArgumentParser(
        description="Removes files with specific formats of interest and also provides an option to remove empty directories. \
            Additionally, it removes bad directories by default. Either one of formats and ref arguments is mandatory. \
            Written by Abhijeet Rao, UCC 2023-2024."
    )

    parser.add_argument('-i', 
                        required=True,
                        type=str, 
                        help="Full path of input directory to summarize")

    parser.add_argument('-formats',
                        type=str,
                        default="",
                        help="Enter the file formats to be removed from the directory structure")

    parser.add_argument('-ref',
                        choices=['y','n'],
                        type=str,
                        default="",
                        help="Would you like to remove empty directories? Enter y/n")     

    parsed_args = parser.parse_args()
    return parsed_args

# Below main function provides the logic on removing files belonging to a specific format
# and removes empty directories if necessary.
def main():

    args = arg_parse()
    input_path = args.i
    log_name_source_ = "remove_bad_"  + str(os.path.basename(input_path)) + time.strftime("_%Y_%m_%dT%H_%M_%S") + ".log"
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source = os.path.join(desktop_logs_dir, log_name_source_)

    if args.formats or args.ref:
        if not os.path.isdir(input_path):
            print(' - Input must be a directory/folder - exiting! - exiting remove.py!')
            generate_log(log_name_source, ' - Input must be a directory/folder - exiting remove.py!')
            sys.exit()
        
        remove_bad_files(input_path, log_name_source)
        
        if args.formats:
            formats = list(str(args.formats).strip().split(' '))    
            for root, subdirs, files in os.walk(input_path):
                
                if files == () or files == []:
                    continue

                for file in files:
                    if str(os.path.splitext(file)[1]).lower() in formats:
                        print(f"File {file} removed from {root}")
                        generate_log(log_name_source, f"File {file} removed from {root}")
                        os.remove(os.path.join(root,file))
        
        if args.ref == 'y':
            for root, subdirs, files in os.walk(input_path):    
                for subdir in subdirs:
                    l = len(os.listdir(os.path.join(root,subdir)))
                    if l == 0:
                        print(f"Empty Folder {subdir} removed from {root}")
                        generate_log(log_name_source, f"Empty Folder {subdir} removed from {root}")
                        os.rmdir(os.path.join(root,subdir))
    else:
        print(' - Either "formats" or "refs" argument is mandatory! - exiting remove.py!')
        generate_log(log_name_source, ' - Either "formats" or "refs" argument is mandatory! - exiting remove.py!')
        sys.exit()

# Below code marks the start of execution of the program.
if __name__ == "__main__":
    main()
                
        
