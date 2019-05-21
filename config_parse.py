import configparser
from collections import OrderedDict
import os
import json

"""
TODO END DOCUMENTATION

Config values:

[drive_api]
Parameters of the google drive api. Leave blank to try automatic setup

[folder]


"""

def get_default_config():
    config = configparser.ConfigParser(allow_no_value=True)
    config_st = OrderedDict()
    # { section_name -> [(key,default_value) , ...] }
    config_st['drive_api'] = []
    config_st['drive_api'].append(('client_id','<here>'))
    config_st['drive_api'].append(('project_id','<here>'))
    config_st['drive_api'].append(('token_uri','<here>'))
    config_st['drive_api'].append(('auth_provider_x509_cert_url','<here>'))
    config_st['drive_api'].append(('client_secret','<here>'))
    config_st['drive_api'].append(('redirect_uris','<here>'))


    config_st['remote'] = []
    config_st['remote'].append(('drive_storage_folder_id',''))
    config_st['remote'].append(('drive_metadata_db_id',''))



    config_st['local_folders'] = []
    config_st['local_folders'].append(('folder_input','files_to_upload'))
    config_st['local_folders'].append(('folder_output','files_to_delete'))
    config_st['local_folders'].append(('mountpoint','virtual_library'))

    config_st['encription'] = []
    config_st['encription'].append(('key','<here>'))


    config_st['virtual_library'] = []
    config_st['virtual_library'].append(('cache_size','32'))


    for section_name,all_options in config_st.items():
        config.add_section(section_name)
        for opt_tuple in all_options:
            key,value = opt_tuple
            config.set(section_name, key, value)
    return config


config_path = 'config.ini'
config = get_default_config()


if not os.path.exists(config_path):
    print('Config not found creating default config.ini Edit this file and rerun')
    # write config to disk
    with open(config_path,'w') as f:
        config.write(f)
    exit(0)

# read config 
with open(config_path) as f:
    config.readfp(f)

# Parse parameters

default_cred_dict = {}
default_cred_dict['installed'] = {k : v for k,v in config['drive_api'].items()}
default_cred_dict['installed']['redirect_uris'] = config['drive_api']['redirect_uris'].split(' , ')

drive_st_folder = config['remote']['drive_storage_folder_id']
drive_metadata_id = config['remote']['drive_metadata_db_id']

folder_input = config['local_folders']['folder_input']
folder_output = config['local_folders']['folder_output']
mountpoint = config['local_folders']['mountpoint']

enc_key = config['encription']['key']

cache_size = int(config['virtual_library']['cache_size'])








