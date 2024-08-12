import os
import sys
import argparse
import time
import re
import shutil
import hashlib
from logger import generate_log, make_desktop_logs_dir, remove_bad_files
from metadata_extractor import format_details, image_exiftool, av_mediainfo

class Arguments():
    pass

def arg_parse():

    '''
    Enter the arguments required 
    '''

    parser = argparse.ArgumentParser(
        description="Generates the csv and txt metadata files for each file format in a directory that is \
            requested in formats parameter during script call and stores txt metadata in exif_txt directory and"
    )

    parser.add_argument('-i', 
                        required=True,
                        type=str, 
                        help="Full path of input directory")
    
    parser.add_argument('-format',
                        required=True, 
                        type=str,
                        default="", 
                        help="Enter the format you would like to package")
    
    parser.add_argument('-uid', 
                        type=str,
                        default="", 
                        help="Enter the destination uid name you would like to assign")
    
    parser.add_argument('-o',
                        type=str,
                        required=True,
                        default="", 
                        help="Full path of output directory to place the uid package")

    parser.add_argument('-supplement',
                        type=str,
                        default="", 
                        help="Enter the supplementary formats you would like to preserve")
    
    parser.add_argument('-kfs',
                        choices=['y', 'n'],
                        required=True,
                        type=str,
                        default="", 
                        help="(KFS - Keep folder structure) : Enter your choice on preserving directory structure for the objects in the destination")
    
    parsed_args = parser.parse_args()

    return parsed_args

# Function taken from ififuncs.py from IFI Scripts repository
def hashlib_md5(filename):
    '''
    uses hashlib to return an MD5 checksum of an input filename
    '''
    read_size = 0
    last_percent_done = 0
    m = hashlib.md5()
    total_size = os.path.getsize(filename)
    with open(str(filename), 'rb') as f:
        while True:
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            m.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write('[%d%%]\r' % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
    md5_output = m.hexdigest()
    return md5_output

def objects_and_supplements_ip(args, log_name_source):
    
    input_path = args.i
    file_formats = args.format_list
    supplement_formats = args.supplement
    output_path = os.path.join(args.o, args.uid)
    objects_folder = args.objects_folder
    supplement_folder = args.supplement_folder
    manifest = os.path.join(output_path, "objects_manifest.md5")

    for root, _, files in os.walk(input_path):
        if files == () or files == []:
            continue

        for file in files:
            file_format = (os.path.splitext(file)[1]).lower()
            if file_format in file_formats:
                file_src = os.path.join(root, file)
                hash_source = str(hashlib_md5(file_src))

                
                if args.kfs == 'n':
                    shutil.copy2(file_src, objects_folder)

                    new_file_name = os.path.basename(root) + "_" + file
                    file_dest = os.path.join(objects_folder, new_file_name)
                    os.rename(os.path.join(objects_folder, file), file_dest)

                else:
                    relative_path = os.path.relpath(root, input_path)
                    dest_dir = os.path.join(objects_folder, relative_path)
                    
                    # Ensure the destination directory exists
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    # Copy the file to the new destination preserving the directory structure
                    new_file_name = file
                    file_dest = os.path.join(dest_dir, new_file_name)
                    shutil.copy2(file_src, file_dest)

                hash_dest = str(hashlib_md5(file_dest))

                if hash_source != hash_dest:
                    print(f"- File {file} not copied properly, integrity compromised. Exiting ip_creator.py")
                    generate_log(log_name_source, f'- File {file} not copied properly, integrity compromised. Exiting ip_creator.py')
                    shutil.rmtree(output_path)
                    sys.exit()
                
                print(f"{file} copied to destination correctly")
                generate_log(log_name_source, f"{file} copied to destination correctly")

                with open(manifest, 'a', encoding='utf-8') as f:
                    rel_path = os.path.relpath(file_dest, output_path)
                    f.write(hash_dest + "  " + str(rel_path))
                    f.write("\n")
            
            elif file_format in supplement_formats:
                file_src = os.path.join(root, file)

                shutil.copy2(file_src, supplement_folder)

                new_file_name = os.path.basename(root) + "_" + file
                file_dest = os.path.join(supplement_folder, new_file_name)
                os.rename(os.path.join(supplement_folder, file), file_dest)
            
    print(f"Manifest file ready for {args.format} files at {manifest}")
    generate_log(log_name_source, f"Manifest file ready for {args.format} files at {manifest}")
    print(f"Finished processing object and supplementary files for {args.format} files")
    generate_log(log_name_source, f"Finished processing object and supplementary files for {args.format} files")
    return

def uid_pattern_check(uid):
    uid_pattern = re.compile(pattern=r"[a-z]{4}\d{4}")
    m = uid_pattern.fullmatch(uid)
    while m is None: #or len(m.group()) != 7:
        print("\nEnter the uid which follows the below rules")
        print("Name format - 4 lowercase alphabets followed by 4 digits (Example : 'doaa4321')")
        uid = input("Please input an uid which follows the above rules: ")
        m = uid_pattern.fullmatch(uid)

    return uid

def main():
    args = arg_parse()
    input_path = args.i
    log_name_source_ = "ip_creator_"  + str(os.path.basename(input_path)) + time.strftime("_%Y_%m_%dT%H_%M_%S") + ".log"
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source = os.path.join(desktop_logs_dir, log_name_source_)
    
    if not os.path.isdir(input_path):
        print(' - Input must be a directory/folder - exiting!')
        generate_log(log_name_source, ' - Input must be a directory/folder - exiting!')
        sys.exit()

    remove_bad_files(input_path, log_name_source)
    
    if args.uid == "":
        uid = input('Please enter the uid name to be created (Do not enter an empty string): ')
        uid = uid_pattern_check(uid)
    else:
        uid = uid_pattern_check(args.uid)
    
    args.uid = uid
    output_path_ = args.o

    os.makedirs(output_path_, exist_ok= True)
    output_path = os.path.join(output_path_, uid)

    if os.path.exists(output_path):
        q = input(f"Warning - {output_path} path already exists, do you want to continue with package creation with this uid? (y/n): ")
        generate_log(log_name_source, f"Warning - {output_path} path already exists, do you want to continue with package creation with this uid? (y/n)")
        generate_log(log_name_source, str(q))
        if q.lower() != 'y':
            print("ip_creator.py - Process Exiting")
            generate_log(log_name_source, "ip_creator.py - Process Exiting")
            sys.exit()
    
    if args.supplement == "":
        q = input("Would you like to preserve supplementary files of specific formats? (y/n): ")
        if q.lower() == 'y':
            supplement = input('Enter supplements list: ')
            generate_log(log_name_source, f"Supplementary formats to be preserved - {supplement}")
            supplement = list(map(str, supplement.strip().split(" ")))
        else:
            supplement = []
            print("No supplmentary formats to be preserved")
            generate_log(log_name_source, "No supplmentary formats to be preserved")
    else:
        supplement = args.supplement
        generate_log(log_name_source, f"Supplementary formats to be preserved - {supplement}")

    args_object = Arguments()

    format = args.format
    ret = format_details(format, "image_format_mapper.csv")
    if ret == "":
        ret = format_details(format, "av_format_mapper.csv")
        if ret == "":
            generate_log(log_name_source, "Enter a proper av or image format to package")
            print("Enter a proper image or av format to package")
            sys.exit()
        else:
            args_object.av = format
            args.format_list = ret
            metadata = av_mediainfo
    else:
        args_object.img = format
        args.format_list = ret
        metadata = image_exiftool

    args_object.i = input_path
    args_object.dest = output_path
    
    os.makedirs(output_path, exist_ok=True)

    objects_folder = os.path.join(output_path, "objects")
    args.objects_folder = objects_folder
    os.makedirs(objects_folder, exist_ok=True)

    metadata_folder = os.path.join(output_path, "metadata")
    args.metadata_folder = metadata_folder
    os.makedirs(metadata_folder, exist_ok=True)

    supplement_folder = os.path.join(output_path, "supplement")
    args.supplement_folder = supplement_folder
    if supplement:
        os.makedirs(supplement_folder, exist_ok=True)
    
    # Creating required objects structure of the information package creation
    objects_and_supplements_ip(args, log_name_source)

    # Calling appropriate metadata extractor function
    metadata(args_object, log_name_source)

    if os.path.exists(supplement_folder):
        if len(os.listdir(supplement_folder)) == 0:
            os.removedirs(supplement_folder)
    
    return

if __name__ == "__main__":
    main()