Lib Cove Web 1 to Lib Cove Web 2 Content Migration Script
=========================================================

To use:

* Deploy new app, including making sure the database migrations run to create the new tables
* Backup database and media folder
* Copy python script into location on the server; edit by hand the values passed to run function to make sure they are correct
* Make sure file permissions on database and media are editable by the script (noting what they are currently)
* Run script
* Put file permissions on database and media back to what they should be
* Run "python manage.py reprocess_everything" in app

