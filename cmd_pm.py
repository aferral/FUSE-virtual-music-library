

import argparse
import random
from data_manager import get_or_create_metadata_database
from drive_utils import download_and_decript

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--list', action='store_true')
	parser.add_argument('--play')
	parser.add_argument('--random', action='store_true')
	parser.add_argument('--query')

	args = parser.parse_args()


	x=get_or_create_metadata_database()

	if args.random:
		r=x.query('select id_file from metadata ORDER BY RANDOM() limit 1;')


		temp_path = 'temp.mp3'
		with open(temp_path,'wb') as f:
			download_and_decript(r, f)
		print(temp_path)

	if args.query:
		result = x.query(args.query)
		print(result)

	if args.list:
		vals=x.list()
		print(vals)


	if args.play:
		id_to_play = args.play
		temp_path = 'temp.mp3'
		with open(temp_path,'wb') as f:
			download_and_decript(id_to_play, f)
		print(temp_path)


