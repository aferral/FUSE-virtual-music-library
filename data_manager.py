import mutagen
import os
import io
import sqlite3

default_sql_lite = 'meta.db'


db_structure_query = """
CREATE TABLE metadata
	(
     id integer primary key,
     TIT2 varchar(30),
     TPE1 varchar(30),
     TPE2 varchar(30),
     TALB varchar(30),
     id_file varchar(50)
    );

"""
db_insert_query = """
INSERT INTO metadata (TIT2,TPE1,TPE2,TALB,id_file) VALUES (:titulo,:artistaA,:artistaB,:album,:id_drive) ;
"""

def create_db_structure(db):
    cursor = db.cursor()
    cursor.execute(db_structure_query)
    db.commit()




def get_metadata(filename):
    return mutagen.File(filename)


class metadata_database:
    def __init__(self,db_obj : sqlite3.Connection):

        self.db_obj = db_obj

    def insert(self):
        pass


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
            return ','.join(map(str,t_row)) # todo escape strings ??
        out_val = '\n'.join(map(format_row,res))
        return out_val

    def list(self):
        out = ""
        c=self.db_obj.cursor()
        c.execute("Select TIT2,TPE1,TPE2,TALB,id_file from metadata")
        for elem in c:
            s, aa, ab, alb, idd = list(map(lambda x : x if x is not None else '-',elem))
            b= aa if aa == ab else "{0},{1}".format(aa,ab)
            out += "{Song} | {Album} | {Band}  ,, {id_drive}\n".format(Band=b, Album=alb, Song=s,id_drive=idd)
        c.close()
        return out



def get_or_create_metadata_database():

    if not os.path.exists(default_sql_lite):
        db = sqlite3.connect(default_sql_lite)
        create_db_structure(db)
    else:
        db = sqlite3.connect(default_sql_lite)

    return metadata_database(db)


def add_to_default_db(folder_with_ids): # folder with files id.out
    x = get_or_create_metadata_database()

    def parse_val(mtd,key_list):
        inter = key_list.intersection(set(mtd.keys()))
        if len(inter) > 0:
            key=inter.pop()
            res=mtd.get(key)
            return ','.join(res) # mutagen handles as list
        else:
            return None

    all_files = os.listdir(folder_with_ids)

    album_tags = set(['album','TALB','ALBUM','Album'])
    track_title_tags = set(['title','TIT2','TITLE','Title'])
    artistA_tags = set(['TPE1','ARTIST','Artist','Author','artist'])
    artistB_tags = set(['albumartist','TPE2','ALBUMARTIST','Album Artist'])

    all_vals = []
    for elem in all_files:
        id_drive = elem.split('.')[0]
        metadata_obj = get_metadata(os.path.join(folder_with_ids,elem))

        TPE1 = parse_val(metadata_obj,artistA_tags)
        TPE2 = parse_val(metadata_obj,artistB_tags)
        TALB = parse_val(metadata_obj,album_tags)
        TIT2 = parse_val(metadata_obj,track_title_tags)
        if (TIT2 is None) and (TPE1 is None) and (TPE2 is None):
            print('{0} No hay suficientes tags para subir a DB arreglar tags '.format(elem))
            continue
        d={'titulo' : TIT2,'artistaA':TPE1,'artistaB':TPE2,'album':TALB,'id_drive':id_drive}
        all_vals.append(d)

    x.batch_insert(all_vals)



if __name__ == '__main__':
    x = get_or_create_metadata_database()
    pass
