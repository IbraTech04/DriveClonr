# DriveClonr
DriveClonr is a simple Python script whose sole task is to clone (Download EVERYTHING) from a user's Google Drive

It was created as a direct response to my graduation of high school, and the imminent threat of my school Google account being deleted 

##Why not use Google Takeout?
Well, that's a great question. For starters, Google Takeout doesn't export shared documents that I don't have access to. Now, as someone who submitted a lot of work on Google Classroom and did a lot of group projects, this was not going to work
I also felt like expanding my knowledge within the Google API, and this activity was perfect!

##Features:
###Auto LongFilePath enabler (Windows only)
Ahh, Windows. Always making my life difficult. Due to the default file path limit in windows being 256 characters, I implemented a check to enable the hidden long file path support within the registry to make sure the app doesn't fail to download files

###Resume from last start
Did your app crash? No worries! Simply select the same directory as you selected previously, and DriveClonr will resume from where it left off!

###C O L O R S 
Cause why not?

###Auto-Export of all Google Workspace documents
Pick between PDF and Office Equivalent, and watch DriveClonr automatically export and download all your Google Workspace documents (Google Docs, Sheets, Slides, etc) in your deisred format
With the exception of Jamboard, which downloads automatically in PDF format, and Drawings, which downloads automatically in PNG format
