
#libraries for working with windows drives
import win32api
import win32file
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import os 
import shutil

# Function for exif data
def photo_exif(file_path):

    # Open the image file
    img = Image.open(file_path)
    
    # Getting data from exif. Added vrbose message is there is no data found
    exif_data = img.getexif()
    if exif_data is None:
        raise ValueError("No EXIF data found in file.")

    # Some exif tag stuff. Uses pillow's TAGS module.
    exif_dict = {}
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        exif_dict[tag_name] = value

    # Get the tag for date and time.
    exif_date = exif_dict.get('DateTime')

    # cleaning date exctracted from exif. 
    clean_time = datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')

    # Extracts camera model from exif, and cleans it up
    exif_model = exif_dict.get('Model')

    #Just in case will put this here
    if not exif_model:
        clean_model = "Unknown Camera"
    else:

        #Removes "EOS" from camera model
        clean_model = exif_model
        clean_model = clean_model.removeprefix("Canon EOS ")
        
    return clean_time, clean_model

# Function to extract the number of a photo
def get_file_number(file_path):
    # Cut the extention
    stem = file_path.stem
    # Next part strips the name to just the number
    parts = stem.split('_')
    if len(parts) >= 2: # this is some weird thing about making sure that list (variable "parts") has at least 2 items. I'm myself not sure why, but it is what it is
        try:
            return int(parts[-1])  # Seclecting last part in the variable (right now it's "IMG" and "00X"), so whatever is last, this command returns as an integer (importnat, since we are doing comarison). [-1] tell python to take last item from whatever list there is
        except ValueError:
            pass
    return 0

#This line getting all the drive letters, remove "\x00" from raw windows responce, and removes last result (actual raw windows response looks like "C:\x00D:\x00E:\x00\x00")
drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]

#Variable outside the scope for the end of a script 
flash_path = None

#Very simple loop for going trough all mounted devices and identifying removable ones
for drive in drives:

    if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:

        #Variable for path name, that script will try to find
        p = Path(drive) / 'DCIM' / '100CANON'
        
        try:

            if p.exists():
                flash_path = p
                break

        #With my cardreader, empty microSD slot appears in system with "device read error". This next exception needed so script can continue without throwing an error
        except Exception:
            continue

# Error in case something goes wrong
if flash_path is None:
    print("Can't find SD card with photos")
    input("press enter to exit")
    exit()

print(f"found {flash_path}")

# Variable for all files 
#all_files = list(flash_path.iterdir())
all_files = [f for f in flash_path.iterdir() if f.is_file()]

# Error if folder is empty 
if not all_files:
    print("SD is found, but there is no photos. Check your SD.")
    input("Press Enter")
    exit()

# This will call the function for getting the number, and will sort it, storing the last one
sorted_files = sorted(all_files, key=get_file_number)
last_file = sorted_files[-1]

# Calling an exif extraction function on the last file
path_date, path_model = photo_exif(last_file)

# Last clean up and craft of a future folder name
date_str = path_date.strftime('%Y-%m-%d')
folder_name = f"{date_str}_{path_model}"

# Now it will take this name, and create a folder where I want it!
target_root = Path("D:/Photo")
target_out_root = Path("D:/photo_out")
target_folder = target_root / folder_name #actual path to the output folders
target_out_folder = target_out_root / folder_name

# Create the folders
target_folder.mkdir(exist_ok=True)
target_out_folder.mkdir(exist_ok=True)

print("--- EXIF READ SUCCESSFUL ---")
print(f"Created folders: {target_folder} and {target_out_folder}")


#Copying files
copied_files = []


for file in all_files:
    dest_file = target_folder / file.name
    try:
        shutil.copy2(file, dest_file)
        copied_files.append((file, dest_file))
        print(f"  Copied: {file.name}")
    except Exception as e:
        print(f"\nCan't copy {file.name}: {e}")
        input("Press Enter")
        exit()

print("--- COPYING WAS SUCCESSFUL ---")
print("Press enter")
exit()