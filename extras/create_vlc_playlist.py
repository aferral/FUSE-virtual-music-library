from data_manager import get_or_create_metadata_database
from mount_m_library import get_folder_structure
import os 
import urllib.parse
from xml.sax.saxutils import escape

"""
Create a vlc compatible playlist with all the music in the database. (Asume that the mountpoint is virtual_library)
"""

text = """<?xml version="1.0" encoding="UTF-8"?>
<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">

	<title>{2}</title>
	<trackList>
    {0}
    </trackList>

    <extension application="http://www.videolan.org/vlc/playlist/0">
    {1}
    </extension>

</playlist>
"""

track_string = """
<track>
<location>file://{file_full_path}</location>
<title>{file_title}</title>
<creator>{file_creator}</creator>
<album>{file_album}</album>
<extension application="http://www.videolan.org/vlc/playlist/0">				<vlc:id>{file_id}</vlc:id>
</extension>
</track>
"""

vlc_item_id = """<vlc:item tid="{file_id}"/>"""



# load files
db_obj = get_or_create_metadata_database()
file_dict,folder_dict = get_folder_structure(db_obj) 

# default params 
mount_point = 'virtual_library'
titulo = 'virtual_library'
track_list_string = ""
ext_ids_string = ""
current_id = 0


base_path = os.path.join(os.getcwd(),mount_point)
urlp = lambda x : x.replace(' ','%20').replace('&','%29')
pv = escape

# Write tracks
for k,v in file_dict.items():
    rel_path = k[1:]
    args = {
            'file_full_path' : urlp(os.path.join(base_path,rel_path)),
            'file_title' : pv(v['Song']),
            'file_creator' : pv(v['Band']),
            'file_album' : pv(v['Album']),
            'file_id' : current_id
            }

    ftrack = track_string.format(**args)
    fvlci = vlc_item_id.format(file_id=current_id)

    current_id += 1
    track_list_string += "{0} \n".format(ftrack)
    ext_ids_string += "{0} \n".format(fvlci)

# save
with open('vlc_playlist.xspf','w') as f:
    f.write(text.format(track_list_string,ext_ids_string,titulo))
