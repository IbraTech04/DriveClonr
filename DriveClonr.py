#DriveClonr V1.0
# by Ibrahim Chehab (@ibratech04)

from __future__ import print_function
from tkinter import filedialog

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

global service

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

except:
    #Make popup telling user to install required libraries
    tkinter.messagebox.showinfo("Error", "To continue, DriveClonr will need to install it's depndencies.\n\nPlease click OK to continue.")
    os.system("pip install -r requirements.txt")

tkinter.messagebox.showinfo("Welcome!", "Welcome to DriveClonr!\n\nThis program will help you clone your PDSB drive contents to your local drive. This includes items in your Google Drive, items shared with you, and any other items you have in your Google Drive.\n\nLet's get started!")

tkinter.messagebox.showinfo("Welcome!", "To begin, please login to your Google Account using the next prompt. Don't worry, your credentials will not be stored on this computer; This is simply an OAuth2 login to your Google Drive. In other words, it's going directly through Google!\n\nClick OK to continue.")

#open file dialog to select destination folder
saveDirectory = None
while saveDirectory == None:
    saveDirectory = filedialog.askdirectory(title="title", parent=None)
    #check if folder is valid
    if saveDirectory == None:
        tkinter.messagebox.showinfo("Error", "Please select a valid folder.")
        saveDirectory = None
print(saveDirectory)
service = initGoogle()

#get about info for the drive

about = service.about().get(fields="user").execute()

saveDirectory += about['user']['emailAddress'].split("@")[0] + " - DriveClonr"
i = 0
#check if folder exists
while (os.path.exists(saveDirectory + str(i))):
    i += 1
if (i > 0):
    saveDirectory += "-" + str(i)

os.mkdir(saveDirectory)

#ask user if they prefer pdf or office equivalent
print("This script can download google workspace documents in the following formats: PDF or their office equivalent.\n\nPlease select the format you would like to download to:")
print("1: Office Equivalent")
print("2: PDF")
fileFormat = None
while fileFormat == None:
    fileFormat = input("Please select the format you would like to download to:")
    #if the input is a valid number
    if (fileFormat.isdigit() and int(fileFormat) in [1, 2]):
        print("Awesome! Now the script can start")
    else:
        print("Please select a valid number")

docsFormats = [["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"], [".docx", ".pdf"]]

slidesFormats = [["application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/pdf"], [".pptx", ".pdf"]]

sheetsFormats = [["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/pdf"], [".xlsx", ".pdf"]]

#get list of all folders in google drive
folders = service.files().list(q="'root' in parents and mimeType = 'application/vnd.google-apps.folder'").execute()

def downloadFiles(folderID, indentAmount, currentDir):
    #get list of all folders in the folderID given
    folders = service.files().list(q="'" + folderID + "' in parents and mimeType='application/vnd.google-apps.folder'").execute()
    
    #get name of current folder
    folderName = service.files().get(fileId=folderID, fields="name").execute()['name']
    os.mkdir(currentDir + "/" + folderName)
    #emumerate through all the folders and recursively call LISTFILES on each folder
    for folder in folders['files']:
        #print folder name with indent
        print("\t"*indentAmount + folder['name'])
        downloadFiles(folder['id'], indentAmount + 1, currentDir + "/" + folderName)
    #get list of all files in the folderID given
    files = service.files().list(q="'" + folderID + "' in parents and mimeType != 'application/vnd.google-apps.folder'").execute()
    #emumerate through all the files and print them
    for file in files['files']:
        print("\t"*indentAmount + file['name'])
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
            request = service.files().export_media(fileId=fileID, mimeType=docsFormats[0][int(fileFormat) - 1])
            fileName = file['name'] + docsFormats[1][int(fileFormat) - 1]
        elif (fileType == "application/vnd.google-apps.presentation"):
            request = service.files().export_media(fileId=fileID, mimeType=slidesFormats[0][int(fileFormat) - 1])
            fileName = file['name'] + slidesFormats[1][int(fileFormat) - 1]
        elif (fileType == "application/vnd.google-apps.spreadsheet"):
            request = service.files().export_media(fileId=fileID, mimeType=sheetsFormats[0][int(fileFormat) - 1])
            fileName = file['name'] + sheetsFormats[1][int(fileFormat) - 1]
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
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
        with open(os.path.join(currentDir, folderName, fileName), 'wb') as f:
            f.write(file.getvalue())
            f.close()

for (i, folder) in enumerate(folders['files']):
    print(i+1, folder['name'])
    folderName = service.files().get(fileId=folder['id'], fields="name").execute()['name']
    downloadFiles(folder['id'], 1, saveDirectory)
    #get list of all files in the root folder
files = service.files().list(q="'root' in parents and mimeType != 'application/vnd.google-apps.folder'").execute()
#emumerate through all the files and print them
for file in files['files']:
    print(file['name'])
    fileID = file['id']
    #get file type
    fileType = file['mimeType']
    if (fileType == "application/vnd.google-apps.shortcut"):
        #get info about shortcut
        originalLocation = service.files().get(fileId=fileID, fields="shortcutDetails").execute()['shortcutDetails']['targetId']
        fileID = originalLocation
        fileType = service.files().get(fileId=fileID, fields="mimeType").execute()['mimeType']
    if (fileType == "application/vnd.google-apps.document"):
        request = service.files().export_media(fileId=fileID, mimeType=docsFormats[0][int(fileFormat) - 1])
        fileName = file['name'] + docsFormats[1][int(fileFormat) - 1]
    elif (fileType == "application/vnd.google-apps.presentation"):
        request = service.files().export_media(fileId=fileID, mimeType=slidesFormats[0][int(fileFormat) - 1])
        fileName = file['name'] + slidesFormats[1][int(fileFormat) - 1]
    elif (fileType == "application/vnd.google-apps.spreadsheet"):
        request = service.files().export_media(fileId=fileID, mimeType=sheetsFormats[0][int(fileFormat) - 1])
        fileName = file['name'] + sheetsFormats[1][int(fileFormat) - 1]
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
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(F'Download {int(status.progress() * 100)}.')
    with open(os.path.join(saveDirectory, fileName), 'wb') as f:
        f.write(file.getvalue())
        f.close()


