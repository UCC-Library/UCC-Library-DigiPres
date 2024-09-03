#!/usr/bin/env python3
import os
import argparse
import time
import sys
import filecmp
from logger import make_desktop_logs_dir, generate_log, remove_bad_files

def arg_parse():

    '''
    Enter the arguments required 
    '''

    parser = argparse.ArgumentParser(
        description="Checks for duplicate files across multiple directory paths provided as input. \
            It curates a list for every file with it's corresponding duplicate file paths. \
            Written by ABhijeet Rao, UCC 2023-2024."
    )

    parser.add_argument('-i', 
                        required=True,
                        type=str,
                        nargs='+', 
                        help="Full path of input directory to summarize") 

    parsed_args = parser.parse_args()
    return parsed_args


def main():

    args = arg_parse()
    input_paths = args.i
    log_name_source_ = "search_duplicates_" + time.strftime("_%Y_%m_%dT%H_%M_%S") + ".log"
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source = os.path.join(desktop_logs_dir, log_name_source_)
    join = os.path.join

    
    files_by_size = {}

    print("Beginning script operations for searching duplicates files in given input directory/directories")
    generate_log(log_name_source, "Beginning script operations for searching duplicates files in given input directory/directories")
    generate_log(log_name_source, f"Input Directories : {input_paths}")

    for input_path in input_paths:
        if not os.path.isdir(input_path):
            print(' - Input must be a directory/folder - exiting! - exiting search_duplicates.py!')
            generate_log(log_name_source, ' - Input must be a directory/folder - exiting search_duplicates.py!')
            sys.exit()

        remove_bad_files(input_path, log_name_source)

        for subroot, subdirs, files in os.walk(input_path):
            for file in files:
                fpath = join(subroot, file)
                size = os.path.getsize(fpath)
                if size not in files_by_size:
                    files_by_size[size] = [fpath]
                else:
                    files_by_size[size].append(fpath)
    
    checked_files = set()

    for fsize in files_by_size:
        files_this_size = files_by_size[fsize]
        L = len(files_this_size)
        if L > 1:
            
            for i in range(0, L):
                fpath1 = files_this_size[i]
                if fpath1 in checked_files:
                    continue
                
                duplicates = []
                
                for j in range(i+1, L):
                    fpath2 =  files_this_size[j]
                    if fpath2 not in checked_files and filecmp.cmp(fpath1, fpath2, shallow=False):
                        duplicates.append(fpath2)
                        checked_files.add(fpath2)
            
                if len(duplicates) > 0:
                    checked_files.add(fpath1)
                    print(f"Duplicates for {fpath1} : {duplicates}\n")
                    generate_log(log_name_source, f"Duplicates for {fpath1} : {duplicates}")
                    del duplicates

if __name__ == "__main__":
    main()