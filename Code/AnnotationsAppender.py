import os
import sys
import json
import csv

OUTPUT_JSON_FILENAME = 'annotations_group.json'
OUTPUT_CSV_FILENAME = 'annotations_group.csv'

'''
combines the json files in a given directory
returns a dictionary with all annotations merged 
'''
def combine_json_in_dir(directory):
	images_w_annotations = {}
	for file in os.listdir(directory):
		if file == OUTPUT_JSON_FILENAME: #skip the merged file
			continue
		elif 'json' not in file: #skip non json files
			print('{0} is not a json file skipping'.format(file))
			continue

		with open(os.path.join(directory, file), 'r') as f:
			line = f.readline()	#we expect the json files to be a single long line

		parsed_json = json.loads(line)

		for k, v in parsed_json.items():
			if k == '_via_settings' or k == 'region':
				print('sorry file: {0}, is not the right type make sure you export annotations as json'.format(file))
				break
			
			#regions is where the annotations are stored if empty file has no annotations
			if v['regions'] != []:
				images_w_annotations[k] = v

	return images_w_annotations

'''
combines csv files in a given directory
returns a header and a list with all annotations merged
'''
def combine_csv_in_dir(directory):
	header = None
	images_w_annotations = []
	for file in os.listdir(directory):
		if file == OUTPUT_CSV_FILENAME: #skip the merged file
			continue
		elif 'csv' not in file: #skip non csv files
			print('{0} is not a csv file skipping'.format(file))
			continue

		with open(os.path.join(directory, file), 'r') as csvfile:
			csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
			#header is the first line it contains the title of the 
			#matching item in the list ex. filename column contains file names
			header = csvreader.__next__()
			rc_index = header.index('region_count')
			for row in csvreader:
				#we want to copy annotations of pictures with at least 1 annotation
				if int(row[rc_index]) > 0: 
					images_w_annotations.append(row)

	return header, images_w_annotations

def main():
	path_to_files = os.path.join('..', 'annotations')

	if sys.argv[1].lower() == 'json':
		annotations = combine_json_in_dir(path_to_files)
		print(annotations)

		annotations_as_json = json.dumps(annotations)
		#right now I think we're just rewriting the entire file each time 
		#would it be worth it to make it only append? 
		with open(os.path.join(path_to_files, OUTPUT_JSON_FILENAME), 'w') as f:
			f.write(annotations_as_json)
	elif sys.argv[1].lower() == 'csv':
		header, annotations = combine_csv_in_dir(path_to_files)
		print(annotations)

		with open(os.path.join(path_to_files, OUTPUT_CSV_FILENAME), 'w') as f:
			csv_writter = csv.writer(f, delimiter=',',
											quotechar = '|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			
			csv_writter.writerow(header)
			for row in annotations:
				csv_writter.writerow(row)


if __name__ == '__main__':
    main()