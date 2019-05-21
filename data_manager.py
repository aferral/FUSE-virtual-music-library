import mutagen
import os
import io
import sqlite3
from config_parse import drive_metadata_id
from drive_utils import download_and_decript
from functools import lru_cache
from datetime import datetime 
default_sql_lite = 'meta.db'


db_structure_query = """
CREATE TABLE metadata
	(
     id integer primary key,
     TIT2 varchar(30),
     TPE1 varchar(30),
     TPE2 varchar(30),
     TALB varchar(30),
     id_file varchar(50) NOT NULL,
     extension varchar(10),
     size integer
    );

"""
db_insert_query = """
INSERT INTO metadata (TIT2,TPE1,TPE2,TALB,id_file,extension,size) VALUES (:titulo,:artistaA,:artistaB,:album,:id_drive,:ext,:size) ;
"""

@lru_cache(maxsize=1)
def get_from_remote():
    download_time = datetime.now()
    with open(default_sql_lite,'wb') as f:
        download_and_decript(drive_metadata_id, f)

    return download_time



def create_db_structure(db):
    cursor = db.cursor()
    cursor.execute(db_structure_query)
    db.commit()




def get_metadata(filename):
    return mutagen.File(filename,easy=True)


class metadata_database:
    def __init__(self,db_obj : sqlite3.Connection):

        self.db_obj = db_obj

    def insert(self,vals):
        c=self.db_obj.cursor()
        c.execute(db_insert_query,vals)
        c.close()
        self.db_obj.commit()


    def batch_insert(self,data_in_list):
        c=self.db_obj.cursor()
        c.executemany(db_insert_query,data_in_list)
        c.close()
        self.db_obj.commit()

    def query(self,string_q):
        c=self.db_obj.cursor()
        c.execute(string_q)
        res=c.fetchall()
        c.close()

        def format_row(t_row):
            return ','.join(map(str,t_row))
        out_val = '\n'.join(map(format_row,res))
        return out_val

    def list(self,as_dict=False):
        
        data=[]

        c=self.db_obj.cursor()
        c.execute("Select TIT2,TPE1,TPE2,TALB,id_file,extension,size from metadata")
        for elem in c:
            s, aa, ab, alb, idd,ext,size = list(map(lambda x : x if x is not None else '-',elem))
            b= aa
            data.append({'Band':b, 'Album':alb, 'Song' : s,'id_drive' : idd,'size' : size,'ext' : ext})
        c.close()


        if as_dict:
            return data
        else:
            out = ""
            for d in data:
                out += "{Song} | {Album} | {Band}  ,, {id_drive}\n".format(**d)
            return out



def get_or_create_metadata_database():

    if not os.path.exists(default_sql_lite):
        db = sqlite3.connect(default_sql_lite)
        create_db_structure(db)
    else:
        db = sqlite3.connect(default_sql_lite)

    # GET FILE FROM DRIVE
    downloaded_when = get_from_remote()
    print('Using db meta from {1} '.format(downloaded_when))

    return metadata_database(db)


def add_metadata(file_path,id_file,size,ext):
    x = get_or_create_metadata_database()

    def parse_val(mtd,key_list):
        inter = key_list.intersection(set(mtd.keys()))
        if len(inter) > 0:
            key=inter.pop()
            res=mtd.get(key)
            return ','.join(res) # mutagen handles as list
        else:
            return None

    album_tags = set(['album','TALB','ALBUM','Album'])
    track_title_tags = set(['title','TIT2','TITLE','Title'])
    artistA_tags = set(['TPE1','ARTIST','Artist','Author','artist'])
    artistB_tags = set(['albumartist','TPE2','ALBUMARTIST','Album Artist'])

    metadata_obj = get_metadata(file_path)

    TPE1 = parse_val(metadata_obj,artistA_tags)
    TPE2 = parse_val(metadata_obj,artistB_tags)
    TALB = parse_val(metadata_obj,album_tags)
    TIT2 = parse_val(metadata_obj,track_title_tags)
    
    assert((TIT2 is not None) or (TPE1 is not None) or (TPE2 is not None)),'{0} No hay suficientes tags para subir a DB arreglar tags '.format(file_path)
        
    d={'titulo' : TIT2,'artistaA':TPE1,'artistaB':TPE2,'album':TALB,'id_drive':id_file,'ext': ext,'size':size}
    x.insert(d)



if __name__ == '__main__':
    x = get_or_create_metadata_database()
    pass
