#!/usr/bin/env python3
import os
import time
import sys
import re
import pandas as pd
import pdfminer.high_level
import argparse
from logger import make_desktop_logs_dir, generate_log

# Below function parses input arguments from the command line provided by the user.
def arg_parse():

    '''
    Enter the arguments required 
    '''

    parser = argparse.ArgumentParser(
        description="This script extracts description content from a given set of pdfs and pushes it to spreadsheets. Written by, Abhijeet Rao, UCC 2023-2024"
    )

    parser.add_argument('-i', 
                        required=True,
                        type=str, 
                        help="Full path of input directory")
    
    parser.add_argument('-start',
                        required=True, 
                        type=int, 
                        help="Enter the page number of the pdf from which the extraction starts")
    
    parser.add_argument('-end', 
                        type=int,
                        required=True, 
                        help="Enter the page number of the pdf at the which the extraction ends")
    
    parser.add_argument('-o',
                        type=str,
                        required=True,
                        default="", 
                        help="Full path of output directory to place the spreadsheet")

    parsed_args = parser.parse_args()

    return parsed_args

# Function to determine the level based on the extent
def determine_level(extent):
    extent_lower = extent.lower()  # Convert to lower case for consistency
    if 'pp' in extent_lower or 'p' in extent_lower:
        return 'Item'
    elif 'items' in extent_lower:
        return 'File'
    return ''

# Function to extract the first sentence from a paragraph
def extract_first_sentence(paragraph):
    match = re.match(r'[^.!?]*[.!?]', paragraph)
    return match.group(0).strip() if match else ''

# Main function to extract the content from pdf and store it in the ecel spreadsheet.
def main():
    args = arg_parse()
    
    desktop_logs_dir = make_desktop_logs_dir()
    join = os.path.join
    

    file_path = args.i
    page_start = args.start
    page_end = args.end
    output_path = args.o

    if not os.path.exists(file_path):
        print(' - Input file does not exist, enter proper file path !')
        generate_log(log_name_source, ' - Input file does not exist, enter proper file path - exiting !')
        sys.exit()
    
    file_name, file_ext = os.path.splitext(file_path)
    file_name = os.path.basename(file_name)

    log_name_source_ = "pdf_extractor_" + file_name + "_" + time.strftime("_%Y_%m_%dT%H_%M_%S") + ".log"
    log_name_source = join(desktop_logs_dir, log_name_source_)

    if not os.path.isfile(file_path) or file_ext != ".pdf":
        print(' - Input must be a file of pdf format !')
        generate_log(log_name_source, ' - Input must be a file of pdf format !')
        sys.exit()

    if not isinstance(page_start, int) or not isinstance(page_end, int) or page_start > page_end:
        print(' - Start and ending page numbers should be positive whole numbers and starting page number should be lesser than ending page number')
        generate_log(log_name_source, ' - Input must be a file of pdf format !')
        sys.exit()
    
    os.makedirs(output_path, exist_ok=True)

    generate_log(log_name_source, f"pdf file to be extracted - {file_path}")
    generate_log(log_name_source, f"Starting page : {page_start}")
    generate_log(log_name_source, f"Page end : {page_end}")

    text = pdfminer.high_level.extract_text(file_path, page_numbers=list(range(page_start - 1, page_end)))
    pattern = r'(?P<paragraph>.+?(?:\n.+?)*?)\n\s*(?P<extent>\d+\s*(?:pp|p|items|ff))'
    regexp = re.compile(pattern, re.IGNORECASE)

    data = []

    for m in regexp.finditer(text):
        paragraph = m.group('paragraph').strip()
        extent = m.group('extent').strip()
        
        cleaned_paragraph = re.sub(r'\s{3,}', ' ', paragraph)

        level = determine_level(extent)
        
        title = extract_first_sentence(cleaned_paragraph)

        data.append({
            'reference column': '',
            'level': level,
            'date': '',
            'title': title,
            'extent': extent,
            'description': cleaned_paragraph
        })

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data, columns=['reference column', 'level', 'date', 'title', 'extent', 'description'])
    output_file = join(output_path, file_name+f"_{page_start}-{page_end}.csv")

    # Save DataFrame to CSV
    df.to_csv(output_file, index=False)

    print(f"Spreadsheet created at {output_file} successfully.")
    generate_log(log_name_source, f"Spreadsheet successfully created at {output_file}")

if __name__ == "__main__":
    main()
