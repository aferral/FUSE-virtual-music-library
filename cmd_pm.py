#!/usr/bin/env python3
import sys
import json
import argparse
import random
from data_manager import get_or_create_metadata_database
from drive_utils import download_and_decript

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Access to files and metadata.')
	parser.add_argument('--list', action='store_true',help='List all the data in db')
	parser.add_argument('--json', action='store_true',help='List all the data in db as json dict')
	parser.add_argument('--play',help='Download and dump song to temp.ext (drive_id req)')
	parser.add_argument('--play_stdout',help='Dowload and write file to stdout (drive_id req)')
	parser.add_argument('--random', action='store_true',help='Download a random file as temp.<ext>')
	parser.add_argument('--query',help='Given a SQL query get results from the db')

	args = parser.parse_args()


	x=get_or_create_metadata_database(verbose=False)

	if args.random:
		result=x.query('select id_file,extension from metadata ORDER BY RANDOM() limit 1;')
		r,ext = result.split(',')

		temp_path = 'temp.{0}'.format(ext)
		with open(temp_path,'wb') as f:
			download_and_decript(r, f)
		print(temp_path)

	if args.query:
		result = x.query(args.query)
		print(result)

	if args.list:
		vals=x.list()
		print(vals)

	if args.json:
		vals=x.list(as_dict=True)
		print(json.dumps(vals))

	if args.play:
		id_to_play = args.play
		temp_path = 'temp.mp3'
		with open(temp_path,'wb') as f:
			download_and_decript(id_to_play, f)
		print(temp_path)

	if args.play_stdout:
		id_to_play = args.play_stdout
		download_and_decript(id_to_play, sys.stdout.buffer)
