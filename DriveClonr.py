#DriveClonr V1.4
# by Ibrahim (@ibratech04)
# No warranty, use at your own risk (duh...)
# Altho chances are it'll be fine, i've tested it thoroughly, on windows though.
# This program is free software: you can redistribute it and/or modify freely. Just make sure to give credit to the original author (aka me :D)
# This program is not registered as a trademark, and contains zero copyright, patents, or other intellectual property rights. 
from __future__ import print_function
from mmap import PAGESIZE
from fileinput import filename
from tkinter import filedialog
import os
import time
import winreg
from colorama import Fore

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

DOCS_FORMATS = [["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"], [".docx", ".pdf"]]

SLIDES_FORMATS = [["application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/pdf"], [".pptx", ".pdf"]]

SHEETS_FORMATS = [["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/pdf"], [".xlsx", ".pdf"]]

NOT_ALLOWED_IN_FILENAME = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]
failedFiles = []

global service

longFilePaths = True

#Smart import - Try and import required libraries, if it fails run os.system to install them
import tkinter.messagebox
try:
    import os.path
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaIoBaseDownload
    import io
    import shutil
    from cleantext import clean
    #import refresherror from google 
    from google.auth.exceptions import RefreshError
except:
    #Make popup telling user to install required libraries
    print("Installing required libraries... Please wait")
    os.system("pip install -r requirements.txt")
    import os.path
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaIoBaseDownload
    import io
    import shutil
    from cleantext import clean
    

def initGoogle():
    """Shows an authorization popup to the user, and returns the credentials"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')

def clearConsole():
    os.system('cls' if os.name=='nt' else 'clear')

clearConsole()

print(Fore.BLUE + "DriveClonr V1.4")
print("by Ibrahim Chehab (@ibratech04)")
print("github.com/ibratech04")
time.sleep(3)

clearConsole()

#check if credentials.json exists - if it doesn't then the user hasn't setup the proper credentials in a google cloud project
if (not os.path.isfile("credentials.json")):
    print(Fore.RED + "Error: Crednetials file not found. Please create a new Google Cloud project, enable the Google Drive API, and create a credentials.json file in the same directory as this program.")
    input("Press enter to exit...")
    exit()

print(Fore.GREEN + "Welcome to DriveClonr!\nThis program will help you clone your Google Drive contents to your computer. This includes files in your Google Drive, files shared with you, and Google Workspace documents!\nLet's get started!\n")

if (not os.path.exists("token.json")):
    print(Fore.YELLOW + "To begin, please login to your Google Account using the next prompt. You will be warned that this app is unverified; That's because we don't have time to verify the app with Google. Ignore all the warnings and sign in as normal - I can assure you it's safe!")

try:
    service = initGoogle()
except RefreshError as e:
    #delete token.json file if it exists
    if os.path.exists('token.json'):
        print("Refreshing Token. Please re-login to Google Drive.")
        os.remove('token.json')
        service = initGoogle()
    else:
        print("An unknown error occurred: " + str(e))
        print("Check your internet connection and try again")
        print("Try and delete the token.json file if it exists")
        input("Press enter to exit...")
        exit()

about = service.about().get(fields="user").execute()
print(Fore.GREEN + "Logged in as " + about['user']['displayName'])
print(Fore.GREEN + f"Hi {about['user']['displayName']} ({about['user']['emailAddress']})! Welcome to DriveClonr! To continue, Please select the folder you want to clone to. A folder selection dialogue should've launched. If you don't see it, try using Alt + Tab - Sometimes it hides behind other windows or is minimized. The title should read \"Please select a directory to clone to\" \n")

#open file dialog to select destination folder
saveDirectory = None
while saveDirectory == None: # Loop until user selects a valid directory
    saveDirectory = filedialog.askdirectory(title="Please select a directory to clone to", parent=None, initialdir=os.getcwd(), mustexist=True)
    #check if folder is valid
    if saveDirectory == None or saveDirectory == "":
        tkinter.messagebox.showinfo("Error", "Please select a valid folder.")
        saveDirectory = None
#get about info for the drive
about = service.about().get(fields="storageQuota").execute()

#get the user's drive size

size = about['storageQuota']['usage']
#convert size to gigabytes
size = int(size) / (1024 * 1024 * 1024)
about = service.about().get(fields="user").execute()
saveDirectory = os.path.join(saveDirectory, about['user']['emailAddress'].split("@")[0] + " - DriveClonr")

clearConsole()
#ask user if they're ready to continue
print("\nYou have selected the following folder: " + saveDirectory)
#round the size to 2 decimal places
size = round(size, 2)
print(Fore.YELLOW + "This will take approximately " + str(size) + " GB of space on your computer")
#check if user has enough space on their computer
#get free space
total, used, freeSpace = shutil.disk_usage(saveDirectory.split("/")[0])
freeSpace = freeSpace / (1024 * 1024 * 1024)
freeSpace = round(freeSpace, 2)
if (size > freeSpace):
    print(Fore.RED + "\nYou do not have enough space on your computer to clone this drive. Please select a different drive, or free up some space and try again. You need to free up at least " + str(size) + " GB of space on your computer")
    #calculate how much more space is required
    moreSpace = size - freeSpace
    print(Fore.YELLOW + "You need to free up at least " + str(moreSpace) + " GB of space on your computer")
    input("Press enter to exit...")
    exit()
else:
    print(Fore.YELLOW + f"You have {freeSpace} GB of free space on your computer")
    print(Fore.YELLOW + f"You will have approxamately {freeSpace - size} GB of free space after cloning")
    print(Fore.RED + "Note: Some files aren't accounted for when calculating how big your Google Drive is (Google Docs/Slides/Sheets), but when you clone them they will take up space. So this number may increase.\n")
    print(Fore.RED + "Note #2: This script does not back up Google Sites and Google Forms files\n")
    print(Fore.GREEN + "Without further ado, let's clone your drive!\n")
    print("Press enter to continue...")
    input()

if (not os.path.exists(saveDirectory)):
    os.mkdir(saveDirectory)
clearConsole()

#check if long file paths are enabled if the os is windows
if (os.name == "nt"):
    #navigate to Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem and get the value of LongPathsEnabled
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\\CurrentControlSet\\Control\\FileSystem")
    longPaths = winreg.QueryValueEx(key, "LongPathsEnabled")
    if (longPaths[0] == 0):
        print(Fore.RED + "Long file paths are disabled. This may cause problems when cloning your drive. You can either enable long file paths, or shrink file names to fit into Windows' 255 character limit.\n")
        print(Fore.GREEN + "Option 1: Enable long file paths (Recommended). This option will enable long file paths within your operating system and allow you to clone your drive without shrinking file names.\n")
        print(Fore.YELLOW + "Option 2: Shrink file names (Not Reccomended). This option will shrink file names to fit into Windows' 255 character limit, however may still cause errors depending on how large your drive is. It's more of a bandaid solution\n")
        num = None
        while num is None:
            num = input(Fore.RED + "Please select an option: ")
            if (num == "1"):
                os.system("disable-file-limit.reg")
                longFilePaths = True
                print("Long file paths enabled")
                print("Please restart your computer to apply the changes")
                input("Press enter to exit...")
            elif (num == "2"):
                longFilePaths = False
            else: 
                num = None
                print(Fore.RED + "Invalid option. Please select an option: ")
        
#ask user if they prefer pdf or office equivalent
print(Fore.CYAN + "DriveClonr can download Google Workspace (Google Docs/Sheets/Slides) in either PDF or their Office equivalent (Word, PowerPoint, Excel). Please select which format you'd prefer\n")
print(Fore.GREEN + "1: Office Equivalent (Word - docx, Excel - xlsx, PowerPoint - pptx) - Recommended; You will still be able to edit and view these files, however they may look slightly different font/layout-wise. They may also fail to export due to them being too big, so keep that in mind\n")
print(Fore.RED + "2: PDF - Not recommended; You won't be able to edit these files easily, however they will retain their layout perfectly. For the most part should not fail to export\n")

fileFormat = None
while fileFormat == None:
    fileFormat = input(Fore.YELLOW + "Please select the format you would like to download to:")
    #if the input is a valid number
    if (fileFormat.isdigit() and int(fileFormat) in [1, 2]):
        print(Fore.GREEN + "Awesome! Now the script can start")
    else:
        print(Fore.RED + "Please select a valid number")
        fileFormat = None

time.sleep(2)
clearConsole()
#get list of all folders in google drive
response = service.files().list(q="'root' in parents and mimeType = 'application/vnd.google-apps.folder'").execute()
folders = response.get('files')
nextPageToken = response.get('nextPageToken')
while nextPageToken:
    response = service.files().list(q="'root' in parents and mimeType = 'application/vnd.google-apps.folder'", pageToken=nextPageToken).execute()
    folders.extend(response.get('files'))
    nextPageToken = response.get('nextPageToken')
#method which takes a filename and shortens it, while maintaining the extension
def shortenFileName(fileName):
    if (longFilePaths):
        return fileName
    else:
        splitName = fileName.split('.')
        fileNameWithoutExtension = fileName[:-(len(splitName[-1]))]
        fileNameWithoutExtension = fileNameWithoutExtension[:30]
        fileNameWithoutExtension += "." + splitName[-1]
        return fileNameWithoutExtension 

#Method which takes a folder ID, and uses DFS to recursively downloads all files in that folder
def dfsDownload(folderID, currentDir):
    try:
        #get list of all folders in the folderID given
        response = service.files().list(q="'" + folderID + "' in parents and mimeType='application/vnd.google-apps.folder'").execute()
        folders = response.get('files')
        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = service.files().list(q="'" + folderID + "' in parents and mimeType='application/vnd.google-apps.folder'", pageToken=nextPageToken).execute()
            folders.extend(response.get('files'))
            nextPageToken = response.get('nextPageToken')
        #get name of current folder
        folderName = service.files().get(fileId=folderID, fields="name").execute()['name']
        folderName = clean(folderName, no_emoji=True) #remove emojis from name
        if (not os.path.exists(os.path.join(currentDir, folderName))):
            os.mkdir(os.path.join(currentDir,folderName))
        #emumerate through all the folders and recursively call LISTFILES on each folder
        for folder in folders:
            #print folder name with indent
            print(Fore.GREEN + "Found new folder: " + folder['name'])
            dfsDownload(folder['id'], os.path.join(currentDir, folderName))
        #get list of all files in the folderID given
        response = service.files().list(q="'" + folderID + "' in parents and mimeType != 'application/vnd.google-apps.folder'").execute()
        files = response.get('files')
        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = service.files().list(q="'" + folderID + "' in parents and mimeType != 'application/vnd.google-apps.folder'", pageToken=nextPageToken).execute()
            files.extend(response.get('files'))
            nextPageToken = response.get('nextPageToken')
        #emumerate through all the files and print them
        for file in files:
            try:
                print(Fore.YELLOW + "Downloading: " + file['name'])
                #download file
                #get file id
                fileID = file['id']
                #get file type
                fileType = file['mimeType']
                if (fileType == "application/vnd.google-apps.shortcut"):
                    #get info about shortcut
                    originalLocation = service.files().get(fileId=fileID, fields="shortcutDetails").execute()['shortcutDetails']['targetId']
                    fileID = originalLocation
                    fileType = service.files().get(fileId=fileID, fields="mimeType").execute()['mimeType']
                if (fileType == "application/vnd.google-apps.document"):
                    request = service.files().export_media(fileId=fileID, mimeType=DOCS_FORMATS[0][int(fileFormat) - 1])
                    fileName = file['name'] + DOCS_FORMATS[1][int(fileFormat) - 1]
                elif (fileType == "application/vnd.google-apps.presentation"):
                    request = service.files().export_media(fileId=fileID, mimeType=SLIDES_FORMATS[0][int(fileFormat) - 1])
                    fileName = file['name'] + SLIDES_FORMATS[1][int(fileFormat) - 1]
                elif (fileType == "application/vnd.google-apps.spreadsheet"):
                    request = service.files().export_media(fileId=fileID, mimeType=SHEETS_FORMATS[0][int(fileFormat) - 1])
                    fileName = file['name'] + SHEETS_FORMATS[1][int(fileFormat) - 1]
                #check for google drawing
                elif (fileType == "application/vnd.google-apps.drawing"):
                    request = service.files().export_media(fileId=fileID, mimeType="image/png")
                    fileName = file['name'] + ".png"
                #check for jamboard
                elif (fileType == "application/vnd.google-apps.jam"):
                    print("Found Jamboard file")
                    request = service.files().export_media(fileId=fileID, mimeType="application/pdf")
                    fileName = file['name'] + ".pdf"
                else:
                    request = service.files().get_media(fileId=fileID)
                    fileName = file['name']
                if (os.path.exists(os.path.join(currentDir, folderName, fileName))):
                    print(Fore.RED + "File already exists, skipping")
                    continue
                else:
                    #check if file is google forms/sites
                    if (fileType == "application/vnd.google-apps.form" or fileType == "application/vnd.google-apps.site"):
                        print(Fore.MAGENTA + "Skipping: " + file['name'])
                    else:  
                        for i in NOT_ALLOWED_IN_FILENAME:
                            fileName = fileName.replace(i, "")
                        fileName = clean(fileName, no_emoji=True) #remove emojis from name, if any exist
                        
                        file = io.BytesIO()
                        downloader = MediaIoBaseDownload(file, request)
                        done = False
                        
                        if (len(fileName) > 35):
                            fileName = shortenFileName(fileName)
                        
                        while done is False:
                            status, done = downloader.next_chunk()
                            print(F'{int(status.progress() * 100)}%')
                        with open(os.path.join(currentDir, folderName, fileName), 'wb') as f:
                            f.write(file.getvalue())
                            f.close()
            except Exception as e:
                try:
                    print(Fore.RED + "File failed to download: " + fileName + "\nError:"+ str(e))
                    failedFiles.append(fileName + " - Error: ")    #add file name to list of failed files
                    failedFiles.append(str(e))
                except:
                    print("No file name - Other error")
                    failedFiles.append(str(e))    
    except Exception as e:
        try:
            print(Fore.RED + "File failed to download: " + fileName + "\nError:"+ str(e))
            failedFiles.append(fileName + " Error: ")
            failedFiles.append(str(e))
        except:
            print("No file name - Other error")
            failedFiles.append(str(e))

print(Fore.GREEN + "\nStarting clone... This will take a while; Please be patient\n")
print(Fore.YELLOW + "Cloning items in your drive...")

#Enumerate through all the folders and recursively call dfsdownload on each folder - downloads folder contents to the selected directory in the same folder structure as the google drive
try: 
    for (i, folder) in enumerate(folders):
        print(Fore.GREEN + "Found new folder: " + folder['name'])
        folderName = service.files().get(fileId=folder['id'], fields="name").execute()['name']
        dfsDownload(folder['id'], saveDirectory)

    #get list of all files in the root folder
    response = service.files().list(q="'root' in parents and mimeType != 'application/vnd.google-apps.folder'").execute()
    files = response['files']
    nextPageToken = response.get('nextPageToken')
    while nextPageToken:
        response = service.files().list(q="'root' in parents and mimeType != 'application/vnd.google-apps.folder'", pageToken=nextPageToken).execute()
        files.extend(response['files'])
        nextPageToken = response.get('nextPageToken')
    #emumerate through all the files and download
    for file in files:
        try:
            print(Fore.YELLOW + "Downloading: " + file['name'])
            fileID = file['id']
            #get file type
            fileType = file['mimeType']
            if (fileType == "application/vnd.google-apps.shortcut"):
                #get info about shortcut
                originalLocation = service.files().get(fileId=fileID, fields="shortcutDetails").execute()['shortcutDetails']['targetId']
                fileID = originalLocation
                fileType = service.files().get(fileId=fileID, fields="mimeType").execute()['mimeType']
            if (fileType == "application/vnd.google-apps.document"):
                request = service.files().export_media(fileId=fileID, mimeType=DOCS_FORMATS[0][int(fileFormat) - 1])
                fileName = file['name'] + DOCS_FORMATS[1][int(fileFormat) - 1]
            elif (fileType == "application/vnd.google-apps.presentation"):
                request = service.files().export_media(fileId=fileID, mimeType=SLIDES_FORMATS[0][int(fileFormat) - 1])
                fileName = file['name'] + SLIDES_FORMATS[1][int(fileFormat) - 1]
            elif (fileType == "application/vnd.google-apps.spreadsheet"):
                request = service.files().export_media(fileId=fileID, mimeType=SHEETS_FORMATS[0][int(fileFormat) - 1])
                fileName = file['name'] + SHEETS_FORMATS[1][int(fileFormat) - 1]
            #check for google drawing
            elif (fileType == "application/vnd.google-apps.drawing"):
                request = service.files().export_media(fileId=fileID, mimeType="image/png")
                fileName = file['name'] + ".png"
            #check for jamboard
            elif (fileType == "application/vnd.google-apps.jam"):
                request = service.files().export_media(fileId=fileID, mimeType="application/pdf")
                fileName = file['name'] + ".pdf"
            else:
                request = service.files().get_media(fileId=fileID)
                fileName = file['name']
            if (os.path.exists(os.path.join(saveDirectory, fileName))):
                print(Fore.RED + "File already exists, skipping")
                continue
            else:
                #check if file is google forms/sites
                if (fileType == "application/vnd.google-apps.form" or fileType == "application/vnd.google-apps.site"):
                    print(Fore.MAGENTA + "Skipping: " + file['name'])
                else:  
                    for i in NOT_ALLOWED_IN_FILENAME:
                        fileName = fileName.replace(i, "")
                    fileName = clean(fileName, no_emoji=True) #remove emojis from name, if any exist
                    file = io.BytesIO()
                    downloader = MediaIoBaseDownload(file, request)
                    done = False
                    
                    if (len(fileName) > 35):
                        fileName = shortenFileName(fileName)
                    
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(F'{int(status.progress() * 100)}%')
                    with open(os.path.join(saveDirectory, fileName), 'wb') as f:
                        f.write(file.getvalue())
                        f.close()
        except Exception as e:
            try:
                print(Fore.RED + "File failed to download: " + fileName + "\nError:"+ str(e))
                failedFiles.append(fileName + " - Error: ")    #add file name to list of failed files
                failedFiles.append(str(e))
            except:
                print("No file name - Other error")
                failedFiles.append(str(e))    
except Exception as e:
    try:
        print(Fore.RED + "File failed to download: " + fileName + "\nError:"+ str(e))
        failedFiles.append(fileName + " - Error: ")    #add file name to list of failed files
        failedFiles.append(str(e))
    except:
        print("No file name - Other error")
        failedFiles.append(str(e))

#get list of shared files 
clearConsole()
print(Fore.GREEN + "Personal files downloaded, starting shared files...")

response = service.files().list(q="sharedWithMe and mimeType = 'application/vnd.google-apps.folder'").execute()
sharedFolders = response['files']
nextPageToken = response.get('nextPageToken')
while nextPageToken:
    response = service.files().list(q="sharedWithMe and mimeType = 'application/vnd.google-apps.folder'", pageToken=nextPageToken).execute()
    sharedFolders.extend(response['files'])
    nextPageToken = response.get('nextPageToken')
try:
    for (i, folder) in enumerate(sharedFolders):
        print(Fore.GREEN + "Found new folder: " + folder['name'])
        folderName = service.files().get(fileId=folder['id'], fields="name").execute()['name']
        dfsDownload(folder['id'], saveDirectory)

    #get list of all files in the root folder
    response = service.files().list(q="sharedWithMe and mimeType != 'application/vnd.google-apps.folder'").execute()
    files = response['files']
    nextPageToken = response.get('nextPageToken')
    while nextPageToken:
        response = service.files().list(q="sharedWithMe and mimeType != 'application/vnd.google-apps.folder'", pageToken=nextPageToken).execute()
        files.extend(response['files'])
        nextPageToken = response.get('nextPageToken')
    #emumerate through all the files and download
    for file in files:
        try:
            print(Fore.YELLOW + "Downloading: " + file['name'])
            fileID = file['id']
            #get file type
            fileType = file['mimeType']
            if (fileType == "application/vnd.google-apps.shortcut"):
                #get info about shortcut
                originalLocation = service.files().get(fileId=fileID, fields="shortcutDetails").execute()['shortcutDetails']['targetId']
                fileID = originalLocation
                fileType = service.files().get(fileId=fileID, fields="mimeType").execute()['mimeType']
            if (fileType == "application/vnd.google-apps.document"):
                request = service.files().export_media(fileId=fileID, mimeType=DOCS_FORMATS[0][int(fileFormat) - 1])
                fileName = file['name'] + DOCS_FORMATS[1][int(fileFormat) - 1]
            elif (fileType == "application/vnd.google-apps.presentation"):
                request = service.files().export_media(fileId=fileID, mimeType=SLIDES_FORMATS[0][int(fileFormat) - 1])
                fileName = file['name'] + SLIDES_FORMATS[1][int(fileFormat) - 1]
            elif (fileType == "application/vnd.google-apps.spreadsheet"):
                request = service.files().export_media(fileId=fileID, mimeType=SHEETS_FORMATS[0][int(fileFormat) - 1])
                fileName = file['name'] + SHEETS_FORMATS[1][int(fileFormat) - 1]
            #check for google drawing
            elif (fileType == "application/vnd.google-apps.drawing"):
                request = service.files().export_media(fileId=fileID, mimeType="image/png")
                fileName = file['name'] + ".png"
            #check for jamboard
            elif (fileType == "application/vnd.google-apps.jam"):
                request = service.files().export_media(fileId=fileID, mimeType="application/pdf")
                fileName = file['name'] + ".pdf"
            else:            
                request = service.files().get_media(fileId=fileID)
                fileName = file['name']
            if (os.path.exists(os.path.join(saveDirectory, fileName))):
                print(Fore.RED + "File already exists, skipping")
                continue
            else:
                #check if file is google forms/sites
                if (fileType == "application/vnd.google-apps.form" or fileType == "application/vnd.google-apps.site"):
                    print(Fore.MAGENTA + "Skipping: " + file['name'])
                else:
                    for i in NOT_ALLOWED_IN_FILENAME:
                        fileName = fileName.replace(i, "")
                    fileName = clean(fileName, no_emoji=True) #remove emojis from name, if any exist
                    
                    file = io.BytesIO()
                    downloader = MediaIoBaseDownload(file, request)
                    done = False
                    if (len(fileName) > 35):
                        fileName = shortenFileName(fileName)
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(F'{int(status.progress() * 100)}%')
                    with open(os.path.join(saveDirectory, fileName), 'wb') as f:
                        f.write(file.getvalue())
                        f.close()
        except Exception as e:
            try:
                print(Fore.RED + "File failed to download: " + fileName + "\nError:"+ str(e))
                failedFiles.append(fileName + " - Error: ")    #add file name to list of failed files
                failedFiles.append(str(e))
            except:
                print("No file name - Other error")
                failedFiles.append(str(e))
except Exception as e:
    try:
        print(Fore.RED + "File failed to download: " + fileName + "\nError:"+ str(e))
        failedFiles.append(fileName + " Error: ")
        failedFiles.append(str(e))
    except:
        print("No file name - Other error")
        failedFiles.append(str(e))
#tell user that the program is done
print(Fore.YELLOW + "Done! Please review the list of failed files below and download them manually:\n")
print(Fore.RED + "Files that failed and their reason:")
i = 0
for file in failedFiles:
    print(file)
    i += 1
    if (i % 2 == 0):
        print("\n")

#make a file called failedFiles and write the list of failed files to it
with open(os.path.join(saveDirectory, "failedFiles.txt"), "w") as f:
    for file in failedFiles:
        f.write(file)
        f.write("\n")
    f.close()

input(Fore.GREEN + "Press enter to exit")

print(Fore.MAGENTA + "Cleaning up...")

#delete token file
os.remove("token.json") #delete token so user can run program again with a token which will last longer
#open file explorer to show user where the files are
os.startfile(saveDirectory)