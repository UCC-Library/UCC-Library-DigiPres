import os
import shutil
import argparse
import subprocess
import sys
import time
import pandas as pd
from logger import make_desktop_logs_dir, generate_log, remove_bad_files
import csv
from pymediainfo import MediaInfo

def format_details(format, file):
    df = pd.read_csv(file, header=0, index_col="format")
    try:
        map_list = df.loc[format, "map_list"]
        mapped_formats = list(map(str.strip, df.loc[format, "map_list"].split(",")))
    except: 
        mapped_formats = ""

    return mapped_formats

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
    
    parser.add_argument('-img', 
                        type=str,
                        default="", 
                        help="Enter the image formats you would like to inspect")
    
    parser.add_argument('-av',
                        type=str,
                        default="", 
                        help="Enter the audio/video (av) formats you would like to inspect")

    parsed_args = parser.parse_args()

    return parsed_args

def mediainfo_to_csv(file_path, csv_path):
    media_info = MediaInfo.parse(file_path)
    data = []

    # Collecting the headers
    headers = set()
    for track in media_info.tracks:
        for key in track.to_data().keys():
            headers.add(key)
    
    headers = sorted(headers)
    
    # Add 'file_path' as the first header
    headers = ['file_path'] + headers

    # Collecting the data
    for track in media_info.tracks:
        row = {header: track.to_data().get(header, '') for header in headers[1:]}  # Skip 'file_path' for now
        row['file_path'] = file_path
        data.append(row)

    # Writing to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

def image_exiftool(args, log_name_source):

    input_path = args.i
    img_formats_list = list(args.img.split(" "))

    print(f"Beginning exiftool processing of target {img_formats_list} image formats")
    generate_log(log_name_source, f" Beginning exiftool processing of target {img_formats_list} image formats")

    for format in img_formats_list:
        if hasattr(args, 'dest'):
            destination_directory = os.path.join(args.dest, "metadata")
        else:
            destination_directory = os.path.join(input_path + "_metadata_" + format[1:])
            
        os.makedirs(destination_directory, exist_ok=True)
        format_detailed_list = format_details(format, r"image_format_mapper.csv")

        csv_path = os.path.join(destination_directory, "exif_csv")
        txt_path = os.path.join(destination_directory, "exif_txt")

        os.makedirs(csv_path, exist_ok=True)
        os.makedirs(txt_path, exist_ok=True)

        print(f'Beginning processing for {format} format')
        generate_log(log_name_source,f' Beginning processing for {format} format')

        remove_bad_files(input_path, log_name_source)

        for root, _, files in os.walk(input_path):
            if files == () or files == []:
                continue
            
            for file in files:
                if str(os.path.splitext(file)[1]).lower() in format_detailed_list:
                    
                    source_file = os.path.join(root, file)
                    dest_file = os.path.basename(root) + "_" + file 
                    exif_csv = os.path.join(csv_path, dest_file)
                    command = f"""\
                    exiftool -csv "{source_file}" > "{exif_csv}.csv"
                    """      
                    subprocess.run(command, shell=True, text=True)

                    exif_txt = os.path.join(txt_path, dest_file)
                    command = f"""\
                    exiftool "{source_file}" > "{exif_txt}.txt"
                    """
                    subprocess.run(command, shell=True, text=True) 
        
        print(f'- csv and txt folders are created successfully for {format} format')
        generate_log(log_name_source, f'- csv and txt folders are created successfully for {format} format')

        try:
            merged_csv = pd.DataFrame()

            for file in os.listdir(csv_path):
                df = pd.read_csv(os.path.join(csv_path, file), header=0)
                merged_csv = pd.concat([merged_csv, df], ignore_index=True)
            
            if hasattr(args, 'dest'):
                csv_file_name = os.path.basename(args.dest) + "_merged.csv"
            else:
                csv_file_name = os.path.basename(input_path) + "_exif_master.csv"

            merged_csv.to_csv(os.path.join(destination_directory, csv_file_name), index=False, encoding='utf-8')
            print(f'Merged csv files into master_csv for {format}')
            generate_log(log_name_source, f' Merged csv files into master_csv for {format}')

        except Exception as e:
            
            print(f'Could not perform the csv files merge operation - \n {e}')
            generate_log(log_name_source, f' Could not perform the csv files merge operation - \n {e}')
            print(f'File causing an error in creating master csv - {file}')
            generate_log(log_name_source, f' File causing an error in creating master csv - {file}')
        
        print(f'Exiting Processing for {format} format')
        generate_log(log_name_source,f' Exiting Processing for {format} format')
    
    print("Exiting exiftool processing of target image formats")
    generate_log(log_name_source, " Exiting exiftool processing of target image formats")
    return

def av_mediainfo(args, log_name_source):

    input_path = args.i
    av_formats_list = list(args.av.split(" "))

    print(f"Beginning mediainfo processing of target {av_formats_list} av formats")
    generate_log(log_name_source, f" Beginning mediainfo processing of target {av_formats_list} av formats")

    for format in av_formats_list:
        if hasattr(args, 'dest'):
            destination_directory = os.path.join(args.dest, "metadata")
        else:
            destination_directory = os.path.join(input_path + "_metadata_" + format[1:])
        
        os.makedirs(destination_directory, exist_ok=True)
        format_detailed_list = format_details(format, r"av_format_mapper.csv")

        csv_path = os.path.join(destination_directory, "mediainfo_csv")
        xml_path = os.path.join(destination_directory, "mediainfo_pbcore")

        os.makedirs(csv_path, exist_ok=True)
        os.makedirs(xml_path, exist_ok=True)

        print(f'Beginning processing for {format} format')
        generate_log(log_name_source,f' Beginning processing for {format} format')

        for root, _, files in os.walk(input_path):
            if files == () or files == []:
                continue

            for file in files:
                if str(os.path.splitext(file)[1]).lower() in format_detailed_list:
                    
                    source_file = os.path.join(root, file)
                    dest_file = os.path.basename(root) + "_" + file 
                    exif_csv = os.path.join(csv_path, dest_file) + "_mediainfo.csv"
                    mediainfo_to_csv(source_file, exif_csv)
                    # command = f"""\
                    # mediainfo -f "{source_file}" > "{exif_csv}_mediainfo.csv"
                    # """      
                    # subprocess.run(command, shell=True, text=True)

                    exif_txt = os.path.join(xml_path, dest_file)
                    command = f"""\
                    mediainfo -f "{source_file}" --Output=PBCore2 > "{exif_txt}_mediainfo.xml"
                    """
                    subprocess.run(command, shell=True, text=True) 
        
        print(f'- csv and xml folders are created successfully for {format} format')
        generate_log(log_name_source, f'- csv and xml folders are created successfully for {format} format')

        try:
            merged_csv = pd.DataFrame()

            for file in os.listdir(csv_path):
                df = pd.read_csv(os.path.join(csv_path, file), header=0)
                merged_csv = pd.concat([merged_csv, df], ignore_index=True)
            
            if hasattr(args, 'dest'):
                csv_file_name = os.path.basename(args.dest) + "_merged.csv"
            else:
                csv_file_name = os.path.basename(input_path) + "_mediainfo_master.csv"
            
            merged_csv.to_csv(os.path.join(destination_directory, csv_file_name), index=False, encoding='utf-8')
            print(f'Merged csv files into master_csv for {format} format')
            generate_log(log_name_source, f' Merged csv files into master_csv for {format} format')

        except Exception as e:
            
            print(f'Could not perform the csv files merge operation - \n {e}')
            generate_log(log_name_source, f' Could not perform the csv files merge operation - \n {e}')
            print(f'File causing an error in creating master csv - {file}')
            generate_log(log_name_source, f' File causing an error in creating master csv - {file}')
    
        print(f'Exiting Processing for {format} format')
        generate_log(log_name_source,f' Exiting Processing for {format} format')
    
    print("Exiting Mediainfo processing of target audio/video formats")
    generate_log(log_name_source, " Exiting Mediainfo processing of target audio/video formats")
    return

def main():
    args = arg_parse()
    input_path = args.i
    log_name_source_ = "metadata_extractor_"  + str(os.path.basename(input_path)) + time.strftime("_%Y_%m_%dT%H_%M_%S") + ".log"
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source = os.path.join(desktop_logs_dir, log_name_source_)
    

    if not os.path.isdir(input_path):
            print(' - Input must be a directory/folder - exiting!')
            generate_log(log_name_source, ' - Input must be a directory/folder - exiting!')
            sys.exit()
    
    if args.img == "" and args.av == "":
            print(' - At least one format must be provided as input')
            generate_log(log_name_source, ' - At least once format must be provided as input')
            sys.exit()    
    
    if args.img:
        image_exiftool(args, log_name_source)
    
    if args.av:
        av_mediainfo(args, log_name_source)

    return

if __name__ == "__main__":
    main()