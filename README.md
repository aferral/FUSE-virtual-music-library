# FUSE virtual music library

Generate a virtual filesystem with all your music, so you can use you favorite music player (VLC for example)
while keeping all the files in drive just downloading what are you currently listening.

Features:

* Bulk upload and encrypt to store in google drive.
* Maintain a sqlite database to store simple metadata and the files ids.
* Command line interface to retrieve any file given SQL queries .
* Create dummy files with only the metadata for quick indexing.
* With FUSE create virtual folders following th


# Requirements

* A google drive account
* python 3.6
* FUSE library (libfuse)

# Install
```
pip install -r req.txt
```

# Configuration

## Manual config
For a manual config first run
```
python config_parse.py
```
then edit config.ini . For details check config_parse.py


## Easy config

Run

```
python config_parse.py
```

then run

```python
import json
from config_parse import get_default_config, config_path
from data_manager import get_or_create_metadata_database,default_sql_lite

config= get_default_config()

# try to configure drive api
print('For the drive API: Go to https://developers.google.com/drive/api/v3/quickstart/python , Press "Enable the drive API" , "Download Client Configuration", Read the Json and paste it below')
json_test = input('Copy paste the json content here  ')
json_data = json.loads(json_test)
for k,v in json_data['installed'].items():
        config['drive_api'][k] = str(v) if type(v) != list else ' , '.join(v)

# try to configure folder id
print('Go to drive, create a folder for storage and copy the id. The id is in the URL https://drive.google.com/drive/folders/<FOLDER_ID>')
folder_id = input('Enter the folder_id  ')
config['remote']['drive_storage_folder_id'] = folder_id

# ask for key
key_string = input('Enter 32 characters as the key for encription. Save the key somewhere if you lose it you wont be able to access the virtualFiles.  ')
config['encription']['key'] = key_string

# create metadata file and upload it
from drive_utils import get_service, encript_and_upload
from data_manager import default_sql_lite, get_or_create_metadata_database

db = get_or_create_metadata_database(init=True)
path_db = default_sql_lite

s=get_service(cred_dict=json_data)
id_meta=encript_and_upload(path_db,'meta.enc',e_key=key_string,drive_s=s,parent_folder=folder_id)
config['remote']['drive_metadata_db_id'] = id_meta

# write config to disk
with open(config_path,'w') as f:
        config.write(f)

```

## Config file example


```
[drive_api]
client_id = <data from drive api config>
project_id = <data from drive api config>
token_uri = <data from drive api config>
auth_provider_x509_cert_url = <data from drive api config>
client_secret = <data from drive api config>
redirect_uris = <data from drive api config>
auth_uri = <data from drive api config>

[remote]
drive_storage_folder_id = <google drive id for folder>
drive_metadata_db_id = <google drive id for sqlitedb>


[local_folders]
folder_input = files_to_upload
folder_output = files_to_delete
mountpoint = virtual_library

[encription]
key = <32 chars key>

[virtual_library]
cache_size = 32
```


# Use

## File upload

1. Drop all the files (Check valid_types "drive_utils.py") in the folder_input of the config.ini
2. Run python upload_in_folder.py
3. Wait for it to end

## Get files from terminal
```
python cmd_pm.py
```

```
usage: cmd_pm.py [-h] [--list] [--play PLAY] [--random] [--query QUERY]

Access to files and metadata.

optional arguments:
  -h, --help     show this help message and exit
  --list         List all the data in db
  --play PLAY    Download a file given its drive_id. File stored as temp.<ext>
  --random       Download a random file as temp.<ext>
  --query QUERY  Given a SQL query get results from the database
```

## Generate virtual_library

Run
```
python mount_m_library.py
```
This will create a folder in <mountpoint> (check config.ini) with folders (Artist). Each Artist folder has Album folders and the Album folders contain all the music. All the files are just placeholders that will only download when they are opened so you can have a massive library anywhere.

Sometimes music players try to pre load the files, this can be really bad if you have a lot of files. Fortunately you can create a dummy library with only the metadata (so no download are required to index the library). After the indexing you can run without the dummy tag and the files will be downloaded on demand.
```
python mount_m_library.py --dummy
```

VLC also try to pre load files in a playlist to avoid this go to the VLC config playlists ->  disable pre load.

After that you can load the virtual library with:
```
vlc <mountpoint>
```

