# This repository contains python and shell scripts required for the purpose of digital preservation.

## Pre-requisites

1) Ensure mediainfo and exiftool are installed in your system.
2) Ensure python 3.x is installed in your system.
3) Once python 3.x is installed, perform installation of pandas and pymediainfo packages.
   Command to install these packages - "pip3 install pandas pymediainfo"

### Python :

Points to Note : 
    1) Open a bash command prompt before you attempt to execute any of the scripts. 
    2) Logs for each script executed is stored in Desktop in a folder called "ucclibrary_logs" with the name of the log file indicating the script executed along with a timestamp of execution.
    3) Go to the directory where the scripts are stored using the command "cd". Example - cd "/home/user/ucc_library".
    4) To display the parameters accepted by a python script, use the following command "python3 <script_name>.py -h". The "-h" stands for help.
    
Scripts :
1) folder_summary.py - 
    Summary : 
    
    The purpose of this script is to summarise the different formats available in a specific directory. The script automatically parses the contents recursively. It summarizes the different file formats present in the directory and it's sub-directories along with return the space occupied by each file format in Megabytes (MB). These details are diplayed both in the command window and the logs.

    Argument accepted by this script :
    
    1) -i : Input (Absolute) path of the directory to summarize. 
        (Required Parameter)
        
    Example command to execute the script in the command window :

    ```bash
    python3 folder_summary.py -i "/home/user/directory1"
    ```
2) metadata_extractor.py - 
    Summary :
    
    The purpose of this script is to extract the metadata of specfic file format/formats of interest using exiftool (for image formats) or mediainfo (for av formats) tool and store the metadata details for each file in a csv file and a txt file (for image formats) or a xml file (for av formats). The list of image or av formats supported by the script could be viewed in the "format" column of av_format_mapper.csv and image_format_mapper.csv files. To support additional formats please updated the csv files. The individual csv files are merged together to form a master csv file containing the metadata of all the files for each format of interest.

    Output :
    
    For every format of interest, a separate folder is created with the name "<folder_of_interest>_metadata_<format_of_interest>" which is placed right beside the input folder the script will be working on.

    Two subdirectories are created inside the output folder named exiftool_csv and exiftool_txt for image formats or mediainfo_csv and mediainfo_pbcore for av format. Correspondingly, individial csv files and txt/xml files are placed for every input file. The master csv file is placed inside the output folder.

    Note : 
    
    Always run folder_summary.py first to understand the formats present in the input directory of interest and refer to the "format" column (image/av)_format_mapper.csv files and use the exact values in the arguments for this script.

    Arguments accepted by this script :
    
    1) -i : Input (Absolute) path of the directory to inspect. 
                    (Required Parameter)
    2) -img :  Enter the image format/formats to inspect
    3) -av : Enter the av format/formats to inspect
    
    Either one of -img or -av has to be entered for the script execute. Both -img and -av could be used together as well. 

    Example commands to execute the script in the command window :

    ```bash
    python3 folder_summary.py -i "/home/user/directory1" -img ".jpg"
    python3 folder_summary.py -i "/home/user/directory1" -av ".mp3"
    python3 folder_summary.py -i "/home/user/directory1" -img ".jpg .png"
    python3 folder_summary.py -i "/home/user/directory1" -av ".mp3 .mp4"
    python3 folder_summary.py -i "/home/user/directory1" -img ".jpg .png" -av ".mp3 .mp4"
    ```

    3) ip_creator.py -
    Summary : 
    
    The purpose of this script is to create a package wherein a specific format of interest (av/image) is copied and stored inside the "objects" folder created inside the output directory - "<destination_directory>/<uid>". An optional argument is used to decide on perform a simple copy of the file or copy the file along with preserving it's original directory structure from the source to the destination. Metadata extraction is done with the help of metadata_extractor.py and stored in the "metadata" folder created in the destination directory. Optionally, supplementary files could be stored in the "supplement" folder.
        
    Output : 
    1) <output-directory>/objects - Copy of files of a specfic format (av/image) of interest 
    2) <output-directory>/objects_manifest.md5 - Stores the md5 checksums of all the files in objects.
    3) <output-directory>/metadata - contains sub-directories of csv and txt/xml files of metadata generated by metadata_extractor.py functions.
    4) <output-directory>/supplement - Optionally present if there are supplements to be saved.
        
    Note : 
    
    1) Always run folder_summary.py first to understand the formats present in the input directory of interest and refer to the "format" column (image/av)_format_mapper.csv files and use the exact values in the arguments for this script.
        
    Arguments accepted by this script :

    1) -i : Input (Absolute) path of the directory to inspect. 
        (Required Parameter)
    2) -o : Output (Absolute) path of the directory to create the uid package. 
        (Required Parameter)
    3) -uid : uid name to be provided in command-line or dynamically entered by user during code execution. A folder of this name is created in the output path specified by -o.
        (Optional in command line argument, mandatory user input during execution)
    4) -format : The file format of interest to be packaged.
        (Required Parameter) 
    5) -supplement: Specfic supplementary file formats to be stored.
        (Optional)
    6) -kfs : Preserve the input folder structure when copying files to objects directory.
        (Optional)

    Example commands to execute the script in the command window :

    ```bash
    python3 ip_creator.py -i "/home/user/directory1" -o "/home/user/directory4" -uid "dooa1212" -format ".jpg" -supplement ".pdf" -p
    python3 ip_creator.py -i "/home/user/directory1" -o "/home/user/directory4" -uid "dooa1212" -format ".tif"
    python3 ip_creator.py -i "/home/user/directory1" -o "/home/user/directory4" -uid "dooa1212" -format ".jpg" -supplement ".xlsx .pdf"
    ```
    
    4) logger.py -
    
    Summary :
    
    This script contains functions necessary to log all the above script runs.


## Bash : 
    
    Points to note :
    
    1) Open a bash command prompt before you attempt to execute any of the scripts.
    2) Logs and Manifests for each script executed are stored in Desktop in a folder called "ucclibrary_logs" and "ucc_moveit_manifests" with the name of the log file indicating the script executed along with a timestamp of execution and name of the manifest file indicating the folder the script worked on.
    3) Go to the directory where the scripts are stored using the command "cd". 
        Example - cd "/home/user/ucc_library".

    Scripts : 

    1) manifest.sh -
    
    Summary :
    
    The purpose of this bash script is to generate the md5 checksum manifest file for each and every file for a given directory of interest and store all the checksum results in a single file. An optional parameter "sidecar" could be passed while calling the script of execution with which the log file and manifest file is stored right beside the directory on which the script will work on. If sidecar isn't passed the logs and checksum file are stored in logs and manifest folder respectively.
        
    Output :
    
    <input-folder>_manifest.md5 file
        
    Arguments accepted by this script : 
    
    1) -s : sidecar argument to store logs and checksum beside the directory the script operates on.
        (Optional)
        
    Example commands to execute the script in the command window :
    
    ```bash    
    bash manifest.sh "/home/user/directory1"
    bash manifest.sh "/home/user/directory1" -s
    ```

## Documented by :
###    Abhijeet Rao,
###    M.Sc. Data Science and Analytics,
###    UCC 2023-2024