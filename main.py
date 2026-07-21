
#libraries for working with windows drives
import win32api
import win32file
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import os 

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


#This line getting all the drive letters, remove "\x00" from raw windows responce, and removes last result (actual raw windows response looks like "C:\x00D:\x00E:\x00\x00")
drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]

#Variable outside the scope for the end of a script 
s = None

#Very simple loop for going trough all mounted devices and identifying removable ones
for drive in drives:

    if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:

        #Variable for path name, that script will try to find
        p = Path(drive) / 'DCIM' / '100CANON'
        
        try:

            if p.exists():
                print(p)
                s = p
                break

        #With my cardreader, empty microSD slot appears in system with "device read error". This next exception needed so script can continue without throwing an error
        except Exception:
            continue

if s is None:
    print("No removable drives with photos found")


