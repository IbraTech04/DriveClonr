#DriveClonr V1.0
# by Ibrahim Chehab (@ibratech04)
# No warranty, use at your own risk (duh...)
# This program is free software: you can redistribute it and/or modify freely. Just make sure to give credit to the original author (aka me :D)

# Shoutout to the gr12 guidance classroom for making such a terrible guide on how to export your files, promting me to make DriveClonr

from __future__ import print_function
from fileinput import filename
from tkinter import filedialog
import os
from colorama import Fore
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

DOCS_FORMATS = [["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"], [".docx", ".pdf"]]

SLIDES_FORMATS = [["application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/pdf"], [".pptx", ".pdf"]]

SHEETS_FORMATS = [["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/pdf"], [".xlsx", ".pdf"]]

NOT_ALLOWED_IN_FILENAME = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]
failedFiles = []

global service

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

print(Fore.GREEN + "Welcome to DriveClonr!\nThis program will help you clone your Google drive contents to your local drive. This includes items in your Google Drive, items shared with you, and Google Workspace documents\nLet's get started!\n")

print(Fore.YELLOW + "To begin, please login to your Google Account using the next prompt. Don't worry, your credentials will not be stored anywhere except this computer; \nThis is simply an OAuth2 login to your Google Drive. In other words, it's going directly through Google! \nYou will notice that the program will warn you about being unverified. Due to the tight time frame, I was unable to verify the app with Google. Ignore any warnings the login provides and simply continue as normal\n")

service = initGoogle()
about = service.about().get(fields="user").execute()

print(Fore.GREEN + f"Hi {about['user']['emailAddress']}! Welcome to DriveClonr. Now, please select the folder you want to clone to\n")

#open file dialog to select destination folder
saveDirectory = None
while saveDirectory == None: # Loop until user selects a valid directory
    saveDirectory = filedialog.askdirectory(title="Please select a directory to clone to", parent=None)
    #check if folder is valid
    if saveDirectory == None or saveDirectory == "":
        tkinter.messagebox.showinfo("Error", "Please select a valid folder.")
        saveDirectory = None
#get about info for the drive
about = service.about().get(fields="storageQuota").execute()

#get hte user's drive size

size = about['storageQuota']['usage']
#convert size to gigabytes
size = int(size) / (1024 * 1024 * 1024)
about = service.about().get(fields="user").execute()
saveDirectory += "/" + about['user']['emailAddress'].split("@")[0] + " - DriveClonr"

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
    exit()
else:
    print(Fore.YELLOW + f"You have {freeSpace} GB of free space on your computer")
    print(Fore.YELLOW + f"You will have approxamately {freeSpace - size} GB of free space after cloning")
    print(Fore.RED + "Note: Some files aren't accounted for when calculating how big your Google Drive is (Google Docs/Slides/Sheets), but when you clone them they will take up space. So this number may increase.\n")
    print(Fore.RED + "Note #2: This script does not back up Google Sites and Google Forms files.\n")
    print("Without further ado, let's clone your drive!\n")

if (not os.path.exists(saveDirectory)):
    os.mkdir(saveDirectory)



#ask user if they prefer pdf or office equivalent
print("DriveClonr can download Google Workspace (Google Docs/Sheets/Slides) in either PDF or their Office equivalent (Word, PowerPoint, Excel). Please select which format you'd prefer\n")
print(Fore.GREEN + "1: Office Equivalent (Word - docx, Excel - xlsx, PowerPoint - pptx) - Recommended; You will still be able to edit and view these files, however they may look slightly different font/layout-wise. They may also fail to export due to them being too big, so keep that in mind\n")
print(Fore.RED + "2: PDF (Everything will get converted to PDF) - Not recommended; You won't be able to edit these files easily, however they will retain their layout perfectly. For the most part should not fail to export\n")
fileFormat = None
while fileFormat == None:
    fileFormat = input(Fore.YELLOW + "Please select the format you would like to download to:")
    #if the input is a valid number
    if (fileFormat.isdigit() and int(fileFormat) in [1, 2]):
        print(Fore.GREEN + "Awesome! Now the script can start")
    else:
        print(Fore.RED + "Please select a valid number")
import time
time.sleep(2)
clearConsole()
#get list of all folders in google drive
folders = service.files().list(q="'root' in parents and mimeType = 'application/vnd.google-apps.folder'").execute()

#Method which takes a folder ID, and uses DFS and recursively downloads all files in that folder
def dfsDownload(folderID, currentDir):
    try:
        #get list of all folders in the folderID given
        folders = service.files().list(q="'" + folderID + "' in parents and mimeType='application/vnd.google-apps.folder'").execute()
        
        #get name of current folder
        folderName = service.files().get(fileId=folderID, fields="name").execute()['name']
        folderName = clean(folderName, no_emoji=True) #remove emojis from name
        if (not os.path.exists(currentDir + "/" + folderName)):
            os.mkdir(currentDir + "/" + folderName)
        #emumerate through all the folders and recursively call LISTFILES on each folder
        for folder in folders['files']:
            #print folder name with indent
            print(Fore.YELLOW + "Found new folder: " + folder['name'])
            dfsDownload(folder['id'], currentDir + "/" + folderName)
        #get list of all files in the folderID given
        files = service.files().list(q="'" + folderID + "' in parents and mimeType != 'application/vnd.google-apps.folder'").execute()
        #emumerate through all the files and print them
        for file in files['files']:
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
                request = service.files().export_media(fileId=fileID, mimeType="application/pdf")
                fileName = file['name'] + ".pdf"
            else:
                request = service.files().get_media(fileId=fileID)
                fileName = file['name']
            if (os.path.exists(currentDir + "/" + folderName + "/" + fileName)):
                print(Fore.RED + "File already exists, skipping")
                continue
            else:
                #check if file is google forms/sites
                if (fileType == "application/vnd.google-apps.form" or fileType == "application/vnd.google-apps.site"):
                    print("Skipping: " + file['name'])
                else:  
                    for i in NOT_ALLOWED_IN_FILENAME:
                        fileName = fileName.replace(i, "")
                    fileName = clean(fileName, no_emoji=True) #remove emojis from name, if any exist
                    
                    file = io.BytesIO()
                    downloader = MediaIoBaseDownload(file, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(F'{int(status.progress() * 100)}%')
                    with open(os.path.join(currentDir, folderName, fileName), 'wb') as f:
                        f.write(file.getvalue())
                        f.close()
                    
                    
    except Exception as e:
        print("File failed to download: " + str(e))
        try:
            failedFiles.append(file['name'])
        except:
            print("No file name - Other error")

print("\nStarting clone... This will take a while; Please be patient\n")

#Enumerate through all the folders and recursively call LISTFILES on each folder - downloads folder contents to the selected directory in the same folder structure as the google drive
try: 
    for (i, folder) in enumerate(folders['files']):
        print("Found new folder: " + folder['name'])
        folderName = service.files().get(fileId=folder['id'], fields="name").execute()['name']
        dfsDownload(folder['id'], saveDirectory)

    #get list of all files in the root folder
    files = service.files().list(q="'root' in parents and mimeType != 'application/vnd.google-apps.folder'").execute()
    #emumerate through all the files and download
    for file in files['files']:
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
        if (os.path.exists(saveDirectory + "/" + fileName)):
            print(Fore.RED + "File already exists, skipping")
            continue
        else:
            #check if file is google forms/sites
            if (fileType == "application/vnd.google-apps.form" or fileType == "application/vnd.google-apps.site"):
                print("Skipping: " + file['name'])
            else:  
                for i in NOT_ALLOWED_IN_FILENAME:
                    fileName = fileName.replace(i, "")
                fileName = clean(fileName, no_emoji=True) #remove emojis from name, if any exist
                
                file = io.BytesIO()
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(F'{int(status.progress() * 100)}%')
                with open(os.path.join(saveDirectory, fileName), 'wb') as f:
                    f.write(file.getvalue())
                    f.close()
except Exception as e:
    print("File failed to download: " + str(e))
    try:
        failedFiles.append(file['name'])
    except:
        print("No file name - Other error")

#get list of shared files 
clearConsole()
print(Fore.GREEN + "Personal files downloaded, starting shared files...")

sharedFolders = service.files().list(q="sharedWithMe and mimeType = 'application/vnd.google-apps.folder'").execute()

try:
    for (i, folder) in enumerate(sharedFolders['files']):
        print("Found new folder: " + folder['name'])
        folderName = service.files().get(fileId=folder['id'], fields="name").execute()['name']
        dfsDownload(folder['id'], saveDirectory)

    #get list of all files in the root folder
    files = service.files().list(q="sharedWithMe").execute()
    #emumerate through all the files and download
    for file in files['files']:
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
        if (os.path.exists(saveDirectory + "/" + fileName)):
            print(Fore.RED + "File already exists, skipping")
            continue
        else:
            #check if file is google forms/sites
            if (fileType == "application/vnd.google-apps.form" or fileType == "application/vnd.google-apps.site"):
                print("Skipping: " + file['name'])
            else:  
                for i in NOT_ALLOWED_IN_FILENAME:
                    fileName = fileName.replace(i, "")
                fileName = clean(fileName, no_emoji=True) #remove emojis from name, if any exist
                
                file = io.BytesIO()
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(F'{int(status.progress() * 100)}%')
                with open(os.path.join(saveDirectory, fileName), 'wb') as f:
                    f.write(file.getvalue())
                    f.close()
except Exception as e:
    print("File failed to download: " + str(e))
    try:
        failedFiles.append(file['name'])
    except:
        print("No file name - Other error")
clearConsole()

#tell user that the program is done
print(Fore.YELLOW + "Done! Please review the list of failed files below:\n")
print(Fore.RED + "Files that failed:")
for file in failedFiles:
    print(file)
#delete token file
os.remove("token.json") #delete token so user can run program again with a token which will last longer
#open file explorer to show user where the files are
os.startfile(saveDirectory)