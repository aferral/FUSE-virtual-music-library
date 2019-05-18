

from data_manager import get_or_create_metadata_database
import os 
from drive_utils import download_and_decript
import json

"""
ALTER TABLE metadata
ADD extension varchar(30);

ALTER TABLE metadata
ADD size integer;

"""

metadata_obj = get_or_create_metadata_database()

etapa_0 = False

lista = metadata_obj.list(as_dict=True) # {'Band':b, 'Album':alb, 'Song' : s,'id_drive' : idd}


out_folder = 'all_files'
os.makedirs(out_folder,exist_ok=True)
if etapa_0:

		print('Procesando {0}'.format(out_path))

		if not os.path.exists(out_path):
			with open(out_path,'wb') as f:
				download_and_decript(file_id, f)

else:

	with open('map_ext.json','r') as f:
		ext_map = json.load(f)

	for d in lista:
		file_id = d['id_drive']
		file_name = "{0}_{1}_{2}.mp3".format(d['Song'],d['Band'],d['Album'])
		out_path = os.path.join(out_folder,file_name) 

		# get size
		size=os.stat(out_path).st_size 

		# get tipo
		ext = ext_map[file_name] 


		data_update={'id_drive':file_id,'ext': ext,'size':size}

		db_update_query = """
		UPDATE metadata SET extension = :ext ,size = :size 
		  WHERE id_file = :id_drive ;
		"""

		# add to db
		print('Filename {0} id_drive {1} ext {2} size {3}'.format(file_name,file_id,ext,size))

		c=metadata_obj.db_obj.cursor()
		c.execute(db_update_query,data_update)
		c.close()
		metadata_obj.db_obj.commit()



