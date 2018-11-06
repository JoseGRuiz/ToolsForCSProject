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
	contributions = []
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
			region_shape_attr = header.index('region_shape_attributes')
			file_contributions = {}
			for row in csvreader:
				#we want to copy annotations of pictures with at least 1 annotation
				#also only accept rect type annotations for now
				if int(row[rc_index]) > 0 and 'rect' in row[region_shape_attr]:
					if row[0] in file_contributions:
						file_contributions[row[0]] += 1
					else:
						file_contributions[row[0]] = 1
					images_w_annotations.append(row)
			contributions.append((file, file_contributions))

	return header, images_w_annotations, contributions

'''
this format is preffered by Ayesha who is writing
the main program, it is a modified subset of the via output
the basic form is file, x, y, x+w, y+h, class
'''
def extract_useful(header, csv_annotations):
	filename_index = header.index('filename')
	region_shape_attr = header.index('region_shape_attributes')
	#region shape attributes are split up into 5 strings
	region_attr = region_shape_attr + 5

	new_annotations = []
	for row in csv_annotations:
		new_row = [row[filename_index]]
		#first 2 are copies of x and y 
		for i in range(1, 3):
			#the number starts 1 after the semicolon
			start_of_num = row[region_shape_attr + i].find(':') + 1
			new_row.append(int(row[region_shape_attr + i][start_of_num:]))
		#last 2 are x+w, and y+h
		#x and y are 2 spaces away from x+w, and y+h respectively
		start_of_num = row[region_shape_attr + 3].find(':') + 1
		new_row.append(new_row[1] + int(row[region_shape_attr + 3][start_of_num:]))
		
		start_of_num = row[region_shape_attr + 4].find(':') + 1
		new_row.append(new_row[2] + int(row[region_shape_attr + 4][start_of_num:-2]))	
	
		#the last string is a bit tricky but same idea works 
		#find the semicolon and then skip over unimportant characters
		#the rest of the string except the last 4 characters is the class name
		start_of_name = row[region_attr].find(':') + 3
		new_row.append(row[region_attr][start_of_name:-4])

		new_annotations.append(new_row)

	new_header = ['filename', 'TopL_x', 'TopL_y', 'BottomR_x', 'BottomR_y', 'class']
	return new_header, new_annotations

def printContributions(contributions):
	"""
	prints usefull information about how each file is contributing to 
	the final merged file
	"""
	for file, file_contributions in contributions:
			print('file {0} contributed {1} annotated pictures to the merged file'.format(
				file, len(file_contributions)))
			individual_annotations = 0
			for annottation in file_contributions:
				individual_annotations += file_contributions[annottation]
			print('\ttotal annotations: {0}'.format(individual_annotations))
			print('\taverage annotations per file: {:.2f}\n'.format(
				individual_annotations / len(file_contributions)))

def main():
	if len(sys.argv) < 3:
		print('error: make sure to call in this form python <path_to_files> <type_of_fies>')
		exit(1)

	path_to_files = sys.argv[1]

	if sys.argv[2].lower() == 'json':
		annotations = combine_json_in_dir(path_to_files)
		#print(annotations)

		annotations_as_json = json.dumps(annotations)
		#right now I think we're just rewriting the entire file each time 
		#would it be worth it to make it only append? 
		with open(os.path.join(path_to_files, OUTPUT_JSON_FILENAME), 'w') as f:
			f.write(annotations_as_json)

		print('succesfully joined json files')
	elif sys.argv[2].lower() == 'csv':
		header, annotations, contributions = combine_csv_in_dir(path_to_files)
		#print(annotations)

		header, annotations = extract_useful(header, annotations)
		with open(os.path.join(path_to_files, OUTPUT_CSV_FILENAME), 'w') as outputcsv:
			csv_writter = csv.writer(outputcsv, delimiter=',',
											quotechar = '|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			
			csv_writter.writerow(header)
			for row in annotations:
				csv_writter.writerow(row)

		print('succesfully joined csv files')
		printContributions(contributions)

if __name__ == '__main__':
    main()