import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import random
from datetime import datetime
import shutil
from utils import encrypt_file, key, decrypt_file
from functools import lru_cache
import hashlib
import os.path
import hashlib
import tempfile
import logging
from config_parse import folder_output, folder_input, drive_st_folder,default_cred_dict, cache_size 

log = logging.getLogger('fuse.log-mixin')
folder_out = folder_output
folder_in = folder_input
os.makedirs(folder_in,exist_ok=True)
os.makedirs(folder_out,exist_ok=True)

valid_types = ['mp3','flac','opus','ogg','m4a']
FOLDER_ID = drive_st_folder
SCOPES = ['https://www.googleapis.com/auth/drive']




def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest() if ashexstr else hasher.digest()

def file_as_blockiter(afile, blocksize=65536):
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)


def calc_checksum(fd):
    fd.seek(0)
    byte_iterable = file_as_blockiter(fd)
    x=hash_bytestr_iter(byte_iterable, hashlib.md5(),ashexstr=True)
    return x




def get_service(cred_dict=None):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if cred_dict is None:
                flow = InstalledAppFlow.from_client_config(default_cred_dict, SCOPES)
            else:
                flow = InstalledAppFlow.from_client_config(cred_dict,SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds,cache_discovery=False)
    return service



def download_file(drive_service, file_id,out_fd):
    log.info('Calling GET')
    request = drive_service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(out_fd, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

def encript_update_file(drive_id, file_path, new_name):
    key_to_use = key
    driver_service = get_service()

    with open(file_path, 'rb') as fd:
        io_temp = io.BytesIO()
        encrypt_file(fd, key_to_use, io_temp)
        file_metadata = {'name': new_name}

        media = MediaIoBaseUpload(io_temp,'/enc')
        metadata['parents'] = [FOLDER_ID]

        file_res = driver_service.files().update(fileId=drive_id, body=metadata,media_body=media,fields='id,md5Checksum').execute()
        checksum = file_res.get('md5Checksum')
        origin_chk = calc_checksum(io_temp)
        assert(checksum == origin_chk)


def upload_file(driver_service,fd,metadata,parent_folder=FOLDER_ID):

    media = MediaIoBaseUpload(fd,'/enc')
    metadata['parents'] = [parent_folder]
    file = driver_service.files().create(body=metadata,media_body=media,fields='id,md5Checksum').execute()
    new_id = file.get('id')
    checksum = file.get('md5Checksum')
    origin_chk = calc_checksum(fd)
    assert(checksum == origin_chk)
    return new_id


def encript_and_upload(file_path,new_name,e_key=None,drive_s=None):
    driver_service = get_service() if drive_s is None else drive_s
    key_to_use = key if e_key is None else e_key

    with open(file_path, 'rb') as f:
        io_temp = io.BytesIO()
        encrypt_file(f, key_to_use, io_temp)
        file_metadata = {'name': new_name}
        new_id = upload_file(driver_service, io_temp, file_metadata)

    return new_id


@lru_cache(maxsize=cache_size)
def download_or_get_cached(file_id):
    temp_io = io.BytesIO()
    drive_service = get_service()
    download_file(drive_service, file_id, temp_io)
    return temp_io


def download_and_decript(file_id, fd_out):
    temp_io = download_or_get_cached(file_id)
    temp_io.seek(0)
    decrypt_file(temp_io, key, fd_out) 
    log.info(download_or_get_cached.cache_info())



def main():
    service = get_service()
    # id carpeta con archivos o que contendra archivos
    query_in_folder = "'13cjZpYDNAy2N_mMh3sdH-muFWpkgzLTQ' in parents"
    query_search_folders = "mimeType = 'application/vnd.google-apps.folder'"


    # Call the Drive v3 API
    results = service.files().list(q=query_in_folder,pageSize=10, fields="nextPageToken, files(id, name,md5Checksum)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

    with open('tt.enc', 'rb') as f:
        file_metadata = {'name': 'tt4.enc'}
        upload_file(service, f, file_metadata)
    # # descarga archivo temporal
    # with open('a.enc', 'wb') as f2:
    #     download_file(service, '1UPeBcDemo9OopoQwkVDHri2WHLC_A82K',f2)

if __name__ == '__main__':
    main()
