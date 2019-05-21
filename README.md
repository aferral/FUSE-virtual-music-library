# Install
pip install -r req.txt


# Configuration


TODO



# Use

First configure VLC in playlists ->  pre load files

then 

python mount_m_library.py <mountpoint> 

Then load all the library with vlc or similar.

vlc <mountpoint>


    print('Now trying to configure (If you want to do it manually just exit and edit config.ini)')

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

    db = get_or_create_metadata_database()
    path_db = default_sql_lite

    s=get_service(cred_dict=json_data)
    id_meta=encript_and_upload(path_db,'db.enc',e_key=key_string,drive_s=s)
    config['remote']['drive_metadata_db_id'] = id_meta

    # write config to disk
    with open(config_path,'w') as f:
        config.write(f)


