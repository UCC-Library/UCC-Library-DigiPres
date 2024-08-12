#!/bin/bash -e
# Written by Abhijeet Rao, UCC 2024

remove_bad_files() {
    local rm_list=(".DS_Store" "Thumbs.db" "desktop.ini")
    local root_dir="$1"
    local log_name_source="$2"

    find "$root_dir" -type f | while read -r file; do
        for i in "${rm_list[@]}"; do
            if [[ "$(basename "$file")" == "$i" ]]; then
                echo "**************** removing: $file"
                echo "EVENT = Unwanted file removal - $file was removed" >> "$log_name_source"
                rm -rf "$file" || echo "Cannot delete as source is read-only, not enough permission to delete"
            fi
        done
    done
}

generate_log() {
    local log_file="$1"
    local message="$2"
    echo "$(date +"%Y-%m-%dT%H:%M:%S ")$(whoami) ${message}" >> "$log_file"
}

make_desktop_logs_dir() {
    local desktop_logs_dir="$HOME/Desktop/ucclibrary_logs"
    mkdir -p "$desktop_logs_dir"
    echo "$desktop_logs_dir"
}

make_desktop_manifest_dir() {
    local desktop_manifest_dir="$HOME/Desktop/ucc_moveit_manifests"
    mkdir -p "$desktop_manifest_dir/old_manifests"
    echo "$desktop_manifest_dir"
}

manifest_file_count() {
    local manifest2check="$1"
    local count_in_manifest=0

    if [ -f "$manifest2check" ]; then
        count_in_manifest=$(wc -l < "$manifest2check")
    fi

    echo $count_in_manifest
}

main() {
    sidecar=false

    while getopts ":s" opt; do
        case $opt in 
            s) 
                sidecar=true
                ;;
            \?)
                echo "Invalid option- $OPTARG" >&2
                exit 1
                ;;
        esac
    done
    shift $((OPTIND-1))

    local source="$1"
    local source_parent_dir
    source_parent_dir=$(dirname "$source")
    local normpath
    local command
    case "$(uname)" in
        "Darwin")
            brew install coreutils
            command="greadlink -f"
            ;;
        "Linux"|"CYGWIN"|"MINGW"|"MSYS")
            command="readlink"
            ;;
    esac
    normpath=$("$command" "$source")
    local relative_path
    relative_path=$(basename "$normpath")
    local log_name_source_="${relative_path}_$(date +"%Y_%m_%dT%H_%M_%S")"
    local manifest
    local log_name_source

    if [ "$sidecar" == true ]; then
        manifest="$source_parent_dir/${relative_path}_manifest.md5"
        log_name_source="$source_parent_dir/${log_name_source_}.log"
    else
        local manifest_="${relative_path}_manifest.md5"
        local desktop_manifest_dir
        desktop_manifest_dir=$(make_desktop_manifest_dir)
        manifest="${desktop_manifest_dir}/${manifest_}"
        local desktop_logs_dir
        desktop_logs_dir=$(make_desktop_logs_dir)
        log_name_source="${desktop_logs_dir}/${log_name_source_}.log"
    fi

    generate_log "$log_name_source" "manifest.sh started"
    
    case "$(uname)" in
        "Darwin")
            generate_log "$log_name_source" "EVENT = Generating manifest: status=started, eventType=message digest calculation, module=$module, agent=OSX"
            ;;
        "Linux")
            generate_log "$log_name_source" "EVENT = Generating manifest: status=started, eventType=message digest calculation, module=$module, agent=Linux"
            ;;
        "CYGWIN"|"MINGW"|"MSYS")
            generate_log "$log_name_source" "EVENT = Generating manifest: status=started, eventType=message digest calculation, module=$module, agent=Windows"
            ;;
    esac

    generate_log "$log_name_source" "Source: $source"
    

    if [ -f "$source" ]; then
        echo -e "\n File checksum only supported for folders not files as of now"
        generate_log "$log_name_source" "Error - manifest.sh attempted for file. Only directories allowed"
        generate_log "$log_name_source" "manifest.sh exit"
        exit 1
    elif [ ! -d "$source" ]; then
        echo -e "$source is either not a directory or it does not exist"
        generate_log "$log_name_source" "$source is either not a directory or it does not exist"
        generate_log "$log_name_source" "manifest.sh exit"
        exit 1
    fi

    remove_bad_files "$source" "$log_name_source"
    
    local source_count
    source_count=$(find "$source" -type f | wc -l)

    if [ -f "$manifest" ]; then
        echo ' - A manifest already exists'
        local count_in_manifest
        count_in_manifest=$(manifest_file_count "$manifest")
        if [[ $source_count -ne $count_in_manifest ]]; then
            echo "This manifest may be outdated as the number of files in your directory does not match the number of files in the manifest"
            generate_log "$log_name_source" "EVENT = Existing source manifest check - Failure - The number of files in the source directory is not equal to the number of files in the source manifest"
            exit 1
        fi
    else
        echo "Generating source manifest"
        generate_log "$log_name_source" "EVENT = Generating source manifest"
        #find "$source" -type f -exec md5 {} \; > "$manifest"

        find "$source" -type f -exec sh -c '
        for file do
        md5 "$file" | awk -F " = " '\''{print $2, substr($1, index($1, "(")+1, length($1)-index($1, "(")-1)}'\'' 
        done
        ' sh {} + > "$manifest"
    fi

    local dirbase
    dirbase=$(dirname "$source")
    escaped_base_dir=$(echo "$dirbase" | sed 's/[\/&]/\\&/g; s/ /\\ /g')
    sed -i '' "s|${escaped_base_dir}/||" "$manifest"

    echo "Manifest created in $manifest"
    generate_log "$log_name_source" "Manifest created in $manifest"
}

main "$@"