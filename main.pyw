
#libraries for working with windows drives
import win32api
import win32file
from pathlib import Path

#This line getting all the drive letters, remove "\x00" from raw windows responce, and removes last result (actual raw windows response looks like "C:\x00D:\x00E:\x00\x00")
drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]




#Very simple loop for going trough all mounted devices and identifying removable ones
for drive in drives:

    if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:

        #Variable for path name, that script will try to find
        p = Path(drive) / 'DCIM' / '100CANON'
        
        try:

            if p.exists():
                print(drive)
                break
            
        #With my cardreader, empty microSD slot appears in system with "device read error". This next exception needed so script can continue without throwing an error
        except (OSError, PermissionError):
            continue

