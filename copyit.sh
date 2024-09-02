#!/bin/bash -e
# Written by [Your Name], UCC 2024

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

# Function to compare two manifest files and handle mismatches
compare_manifests() {
    local src_manifest="$1"
    local dest_manifest="$2"
    local log_name="$3"
    local destination="$4"

    echo "Comparing manifests..."
    generate_log "$log_name" "Comparing manifests"
    
    # Check if manifest files exist before comparing
    if [ ! -f "$src_manifest" ]; then
        echo "ERROR: Source manifest file does not exist: $src_manifest"
        generate_log "$log_name" "ERROR: Source manifest file does not exist: $src_manifest"
        exit 1
    fi

    if [ ! -f "$dest_manifest" ]; then
        echo "ERROR: Destination manifest file does not exist: $dest_manifest"
        generate_log "$log_name" "ERROR: Destination manifest file does not exist: $dest_manifest"
        exit 1
    fi

    if diff_output=$(diff "$src_manifest" "$dest_manifest"); then
        echo "Manifests match. Copy successful."
        generate_log "$log_name" "Manifests match. Copy successful."
    else
        echo "ERROR: Manifests do not match. Differences found:"
        echo "$diff_output"
        generate_log "$log_name" "ERROR: Manifests do not match. Differences found:\n$diff_output"

        # Erase the destination directory since the manifest did not match
        echo "Removing destination directory $destination..."
        rm -rf "$destination"
        generate_log "$log_name" "Destination directory $destination removed due to manifest mismatch."

        # Exit with an error
        exit 1
    fi
}

# Main function
main() {
    local source="$1"
    local destination="$2"

    if [ -z "$source" ] || [ -z "$destination" ]; then
        echo "Usage: $0 <source_directory> <destination_directory>"
        exit 1
    fi

    mkdir -p "$destination"

    local desktop_logs_dir=$(make_desktop_logs_dir)
    local desktop_manifest_dir=$(make_desktop_manifest_dir)
    local log_name="${desktop_logs_dir}/copyit_$(date +"%Y_%m_%dT%H_%M_%S").log"
    local source_manifest="${desktop_manifest_dir}/$(basename "$source")_manifest.md5"
    local dest_manifest="${destination}/$(basename "$destination")_manifest.md5"

    # Create manifest for the source directory
    manifest_creator.sh "$source"

    # Copy the directory or object to the destination
    echo "Copying from $source to $destination..."
    generate_log "$log_name" "Copying from $source to $destination"
    
    if ! cp -r "$source" "$destination"; then
        echo "ERROR: Copy failed."
        generate_log "$log_name" "ERROR: Copy failed."
        exit 1
    fi

    echo "problem spot"

    # Create manifest for the destination directory
    execute=$(manifest_creator.sh "$destination" -s)
    mv "${desktop_manifest_dir}/$(basename "$destination")_manifest.md5" "${destination}/$(basename "$destination")_manifest.md5"

    # Compare the manifests and handle errors if they don't match
    compare_manifests "$source_manifest" "$dest_manifest" "$log_name" "$destination"

    echo "Copy and verification completed successfully."
    generate_log "$log_name" "Copy and verification completed successfully."
}

main "$@"
