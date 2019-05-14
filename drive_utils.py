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

folder_in = 'files_to_upload'
folder_out = 'files_to_delete'
os.makedirs(folder_in,exist_ok=True)
os.makedirs(folder_out,exist_ok=True)
valid_types = ['mp3','flac','opus','ogg','m4a']

FOLDER_ID = '13cjZpYDNAy2N_mMh3sdH-muFWpkgzLTQ'
SCOPES = ['https://www.googleapis.com/auth/drive']


import hashlib

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




def get_service():
    """Shows basic usage of the Drive v3 API.
      Prints the names and ids of the first 10 files the user has access to.
      """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service



def download_file(drive_service, file_id,out_fd):
    request = drive_service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(out_fd, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

def upload_file(driver_service,fd,metadata,parent_folder=FOLDER_ID):

    media = MediaIoBaseUpload(fd,'/enc')
    metadata['parents'] = [parent_folder]
    file = driver_service.files().create(body=metadata,media_body=media,fields='id,md5Checksum').execute()
    new_id = file.get('id')
    checksum = file.get('md5Checksum')
    origin_chk = calc_checksum(fd)
    assert(checksum == origin_chk)
    return new_id


def process_single_file(new_name,old_name):


    if os.path.exists(old_name):
        print('Uploading {0}'.format(old_name))
    else:
        print("No existe archivo {0} en carpeta entrada se asume que ya fue procesado.".format(old_name))
        return None 

    driver_service = get_service()

    with open(old_name, 'rb') as f:
        io_temp = io.BytesIO()
        encrypt_file(f, key, io_temp)
        file_metadata = {'name': new_name}
        new_id = upload_file(driver_service, io_temp, file_metadata)

        #Mover a destino final
        # en este punto renombro al id para futura referencia
        out_path = os.path.join(folder_out,"{0}.out".format(new_id))
        shutil.move(old_name,out_path)
     


def upload_list_and_move(data_list):
    for d in data_list:
        (new_name,old_name) = d['nombre_obj'],d['nombre_old']
        process_single_file(new_name,old_name)

    

def download_and_decript(file_id, fd_out):
    drive_service = get_service()
    temp_io = io.BytesIO()

    download_file(drive_service, file_id, temp_io)
    temp_io.seek(0)
    decrypt_file(temp_io, key, fd_out)



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
