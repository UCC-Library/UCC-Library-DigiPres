#!/bin/bash -e
# Written by Abhijeet Rao, UCC 2023-2024

# Below function calculates the md5 manifest checksum of a file.
calculate_checksum() {
    local file="$1"
    # Extract only the checksum value (MD5)
    md5 "$file" | awk -F " = " '{print $2}'
}

# Below function is used to log script execution steps in a separate file for reference.
generate_log() {
    local log_file="$1"
    local message="$2"
    echo "$(date +"%Y-%m-%dT%H:%M:%S") $(whoami) ${message}" >> "$log_file"
}

# Below function creates the log folder required to store script execution logs.
make_desktop_logs_dir() {
    local desktop_logs_dir="$HOME/Desktop/ucclib_logs"
    mkdir -p "$desktop_logs_dir"
    echo "$desktop_logs_dir"
}

# Below function creates the log folder required to store manifest details of a folder of interest.
make_desktop_manifest_dir() {
    local desktop_manifest_dir="$HOME/Desktop/ucclib_manifests"
    mkdir -p "$desktop_manifest_dir"
    echo "$desktop_manifest_dir"
}

# Below function copies each file from source to destination and verifies the manifest details.
# Files that weren't copied properly are registered in the logs for the user to take action.
copy_files_and_validate() {
    local source_dir="$1"
    local dest_dir="$2"
    local source_manifest="$3"
    local dest_manifest="$4"
    local log_file="$5"
    local failed_files=()
    local total_files=0
    local failed_count=0

    find "$source_dir" -type f | while read -r src_file; do
        total_files=$((total_files + 1))

        # Calculate source file checksum (just the checksum value)
        local src_checksum
        src_checksum=$(calculate_checksum "$src_file")

        # Store relative path for manifest
        local relative_path
        local updated_source_dir
        updated_source_dir=$(dirname "$source_dir")
        relative_path=$(realpath --relative-to="$updated_source_dir" "$src_file")

        # Add checksum to source manifest
        echo "$src_checksum $relative_path" >> "$source_manifest"

        # Determine destination file path
        local dest_file="$dest_dir/$relative_path"

        # Ensure destination directory exists
        mkdir -p "$(dirname "$dest_file")"

        # Copy file to destination
        echo "Copying $src_file to $dest_file"
        cp "$src_file" "$dest_file"

        # Calculate destination file checksum (just the checksum value)
        local dest_checksum
        dest_checksum=$(calculate_checksum "$dest_file")

        # Add checksum to destination manifest
        echo "$dest_checksum $relative_path" >> "$dest_manifest"

        # Compare checksums (checksum values only)
        if [[ "$src_checksum" != "$dest_checksum" ]]; then
            echo "Checksum mismatch for $src_file and $dest_file"
            generate_log "$log_file" "Checksum mismatch for $src_file and $dest_file"
            failed_files+=("$relative_path")
            failed_count=$((failed_count + 1))
        else
            echo "Checksum matched for $src_file"
            generate_log "$log_file" "Checksum matched for $src_file"
        fi
    done

    # Return failed files and count
    echo "${failed_files[@]}"
    return $failed_count
}

# Below function summarises the script execution indicating success if all files were copied properly to the destination
# and indicates fail if not. Failed files are printed for user's reference.
report_summary() {
    local total_files="$1"
    local failed_files=("$@")
    local failed_count="${failed_files[0]}"
    shift 1
    local failed_list=("$@")

    if [[ "$failed_count" -eq 0 ]]; then
        echo "SUCCESS. All checksums match. All of your files have copied successfully to your destination directory with integrity."
        echo "The checksum file manifest is stored next to your destination directory and a copy has been kept in the 'ucc_moveit_manifests' folder on your desktop for your future reference."
    else
        echo "FAIL. Not all checksums match. Some of your files have failed to copy to your destination with integrity."
        echo "The following files have mismatched checksums:"
        
        for failed_file in "${failed_list[@]}"; do
            echo "$failed_file"
        done

        echo "We recommend that you attempt to copy the files again."
    fi
}

# Below code controls the flow of execution of the entire script.
main() {

    local source="$1"
    local dest="$2"

    if [[ ! -d "$source" ]]; then
        echo "$source is either not a directory or does not exist"
        exit 1
    fi

    if [[ ! -d "$dest" ]]; then
        echo "$dest is either not a directory or does not exist, creating it --"
        mkdir -p "$dest"
    fi

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
    normpath=$($command "$source")
    local relative_path
    relative_path=$(basename "$normpath")

    local log_name_source_="${relative_path}_$(date +"%Y_%m_%dT%H_%M_%S")"
    local desktop_logs_dir
    desktop_logs_dir=$(make_desktop_logs_dir)
    local log_file="${desktop_logs_dir}/${log_name_source_}.log"

    # Source manifest (always stored in the ucc_moveit_manifests directory)
    local manifest_="${relative_path}_manifest.md5"
    local desktop_manifest_dir
    desktop_manifest_dir=$(make_desktop_manifest_dir)
    local source_manifest="${desktop_manifest_dir}/${manifest_}"
    echo $source_manifest

    # Destination manifest (either stored in ucc_moveit_manifests or as a sidecar)
    local dest_manifest
    dest_manifest="$dest/${manifest_}"
    echo $dest_manifest

    # Log the start of the process
    generate_log "$log_file" "copyfixity.sh started"
    generate_log "$log_file" "Source: $source"
    generate_log "$log_file" "Destination: $dest"

    # Copy files and validate checksums
    failed_files=$(copy_files_and_validate "$source" "$dest" "$source_manifest" "$dest_manifest" "$log_file")
    failed_count=$?

    # Report summary
    report_summary "$failed_count" "${failed_files[@]}"

    generate_log "$log_file" "File copy and checksum validation completed successfully"
}

main "$@"
