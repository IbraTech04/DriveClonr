# DriveClonr
DriveClonr is a simple Python script whose sole task is to clone (Download EVERYTHING) from a user's Google Drive

It was created as a direct response to my graduation of high school, and the imminent threat of my school Google account being deleted 

## Why not use Google Takeout?
Well, that's a great question. For starters, Google Takeout doesn't export shared documents that I don't have access to. Now, as someone who submitted a lot of work on Google Classroom and did a lot of group projects, this was not going to work. I also felt like expanding my knowledge within the Google API, and this activity was perfect!

## How to run
DriveClonr.py is the main entrypoint for this program. However, before starting this script you need to make your own Google Cloud project with the Google Drive API enabled, then download a credentials.json file and place it in the directory of the project. Without this file, this script will not work

To do this, login to console.cloud.google.com. From there, create a new project. Once you're in the project dashboard, click "Enabled APIs and Servives" in the sidebar. Search for the Google Drive API and enable it

Next, navigate to "Credentials" in the sidebar. Click "Create Credentials" on the top and select "OAuth Client ID". For application type, select "Desktop Application" and name it "DriveClonr". Then click "Create" at the very bottom. 

You'll then be presented with a popup with all the info about your credentials. Select "Download JSON". Save it in your project directory as `credentials.json`
Once that's done, you're all set! 

Simply run DriveClonr.py in your favorite Python debugger and follow the on screen prompts!

## Features:
### Auto LongFilePath enabler (Windows only)
Ahh, Windows. Always making my life difficult. Due to the default file path limit in windows being 256 characters, I implemented a check to enable the hidden long file path support within the registry to make sure the app doesn't fail to download files

### Resume from last start
Did your app crash? No worries! Simply select the same directory as you selected previously, and DriveClonr will resume from where it left off!

### C O L O R S 
Cause why not?

### Auto-Export of all Google Workspace documents
Pick between PDF and Office Equivalent, and watch DriveClonr automatically export and download all your Google Workspace documents (Google Docs, Sheets, Slides, etc) in your deisred format
With the exception of Jamboard, which downloads automatically in PDF format, and Drawings, which downloads automatically in PNG format
