from datetime import datetime
import os
import subprocess
import sys

# Global variables

# Name of your remote storage as defined in Rclone (rclone config) property Name
DRIVE_NAME = "google-drive"

# Name and locations of the passwords file
DB_FILE_NAME = "Data_Base.kdbx"
LOCAL_LOCATION = r"D:\Usuario\Documents\.keepass"
REMOTE_LOCATION = "Keepass"

# Compose full path to local and remote database files
LOCAL_PATH = f"{LOCAL_LOCATION}/{DB_FILE_NAME}"
REMOTE_PATH = f"{REMOTE_LOCATION}/{DB_FILE_NAME}"

# Import and export commands
passwords_export = f"rclone copy {LOCAL_PATH} {DRIVE_NAME}:{REMOTE_LOCATION}"
passwords_import = f"rclone copy {DRIVE_NAME}:{REMOTE_PATH} {LOCAL_LOCATION}"


def get_local_passwords_mtime() -> int:
    try:
        timestamp = int(os.path.getmtime(LOCAL_PATH))
    except FileNotFoundError:
        print("No local passwords database found!\nImporting...\t")
        if subprocess.run(passwords_import, stderr=subprocess.DEVNULL).returncode != 0:
            print("Error importing passwords database, please check your network!")
            sys.exit(1)
        print("Done!\n")
        sys.exit(0)
    print(
        f"Local passwords file last modified: {datetime.fromtimestamp(timestamp)}")
    return timestamp


def get_remote_passwords_mtime() -> int:
    output_command = subprocess.run(
        f"rclone lsl {DRIVE_NAME}:{REMOTE_PATH}", capture_output=True, text=True)
    if output_command.returncode != 0:
        print("No remote passwords database found!")
        print("Exporting...")
        if subprocess.run(passwords_export, stderr=subprocess.DEVNULL).returncode != 0:
            print("Error exporting passwords database, please check your network!")
            sys.exit(1)
        print("Done!\n")
        sys.exit(0)
    date_string = output_command.stdout[10:39]
    date_object = datetime.strptime(date_string[:26], "%Y-%m-%d %H:%M:%S.%f")
    timestamp = int(date_object.timestamp())
    print(
        f"Remote passwords file last modified: {datetime.fromtimestamp(timestamp)}")
    return timestamp


if __name__ == "__main__":
    local_time_file = get_local_passwords_mtime()
    remote_time_file = get_remote_passwords_mtime()
    if local_time_file > remote_time_file:
        print("Local file is newer, uploading...")
        print("Exporting...")
        if subprocess.run(passwords_export, stderr=subprocess.DEVNULL).returncode != 0:
            print("Error exporting passwords database, please check your network!")
            sys.exit(1)
        print("Done")
    elif local_time_file < remote_time_file:
        print("Remote file is newer, downloading...")
        print("Importing...\t")
        if subprocess.run(passwords_import, stderr=subprocess.DEVNULL).returncode != 0:
            print("Error importing passwords database, please check your network!")
            sys.exit(1)
        print("Done!")
    else:
        print("Both files are the same, nothing to do.")
