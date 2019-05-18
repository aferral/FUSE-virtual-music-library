import concurrent.futures
import os
import time
from drive_utils import get_service,upload_file

# genera archivos de prueba con texto
n_gen = 50
folder_test = 'test'
re_gen_random = False
paralel = False

if re_gen_random:

	os.makedirs(folder_test,exist_ok=True)
	for i in range(n_gen):
    		name_test = "{0}.txt".format(i)
    		f_p=os.path.join(folder_test,name_test)
    		os.system("head -c 10000000 /dev/urandom > {0}".format(f_p))
else:
	print("files ready")

all_files = os.listdir(folder_test)
full_paths = [os.path.join(folder_test,x) for x in all_files]

def upload_fun(file_path,new_name):
	driver_s = get_service()
	parent_f='183uApPrNsiQ8D9D0Tvqaf3EHGStx6AoN'
	file_metadata = {'name': new_name}
	with open(file_path,'rb') as f:
		upload_file(driver_s,f,file_metadata,parent_folder=parent_f)



if not paralel:
	st=time.time()
	for ind,f_name in enumerate(full_paths):
		upload_fun(f_name,"{0}.txt".format(ind))
	en=time.time()
	print('No paralel elapsed : {0} '.format(en-st))

else:
	st=time.time()
	with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
		futures = {executor.submit(upload_fun, f_name,ind) : f_name for ind,f_name in enumerate(full_paths)}
		for future in concurrent.futures.as_completed(futures):
			path_t = futures[future]
			try:
				data=future.result()
			except Exception as exc:
				print("Exeption {0} ".format(exc))
			else:
				print("Exito para {0}".format(path_t))

	en=time.time()
	print('PARALEL elapsed : {0} '.format(en-st))
