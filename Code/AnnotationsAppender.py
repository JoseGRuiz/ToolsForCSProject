import os
import sys
import json
import csv
import argparse

#globals for names to use for the merged files
OUTPUT_JSON_FILENAME = 'annotations_group.json'
OUTPUT_CSV_FILENAME = 'annotations_group.csv'
CLASSES_CSV_FILENAME = 'classes.csv'
IGNORE_CSV = [OUTPUT_CSV_FILENAME, CLASSES_CSV_FILENAME]

def combine_json_in_dir(directory):
	"""
	combines the json files in a given directory
	returns a dictionary with all annotations merged

	Args:
	directory: the directory containing the files to merge
	"""
	images_w_annotations = {}
	for file in os.listdir(directory):
		if file == OUTPUT_JSON_FILENAME: #skip the merged file
			continue
		elif 'json' not in file: #skip non json files
			print('{0} is not a json file skipping'.format(file))
			continue

		with open(os.path.join(directory, file), 'r') as f:
			line = f.readline()	#we expect the json files to be a single long line

		#interpret the input as json 
		parsed_json = json.loads(line)

		#make sure the right type of file is used there's a few types
		#of json that can come out of via but only 1 is the right type
		for k, v in parsed_json.items():
			if k == '_via_settings' or k == 'region':
				print('sorry file: {0}, is not the right type make sure you export annotations as json'.format(file))
				break
			
			#regions is where the annotations are stored, if empty file has no annotations
			#@TODO: right now images with no tags simply ignored, might not be the best policy
			#becasue it can be beneficial to keep the empty images in the data 
			if v['regions'] != []:
				images_w_annotations[k] = v

	return images_w_annotations

def combine_csv_in_dir(directory):
	"""
	combines csv files in a given directory
	returns a header and a list with all annotations merged

	Args:
	directory: the directory containing the files to merge
	"""
	header = None
	images_w_annotations = []
	contributions = []
	for file in os.listdir(directory):
		if file in IGNORE_CSV: #skip the merged file
			continue
		elif 'csv' not in file: #skip non csv files
			print('{0} is not a csv file skipping'.format(file))
			continue

		#open the file as a csv file and copy the row 
		with open(os.path.join(directory, file), 'r') as csvfile:
			csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
			#header is the first line it contains the title of the 
			#matching item in the list ex. filename column contains file names
			header = csvreader.__next__()

			#find the index of these desired properties
			#region count is how many regions of the image are annotated(how many boxes)
			#region_shape_attributes is which type of annotation style was used (box, polygon, etc...)
			rc_index = header.index('region_count')
			region_shape_attr = header.index('region_shape_attributes')
			file_contributions = {}
			for row in csvreader:
				#we want to copy annotations of pictures with at least 1 annotation
				#also only accept rect type annotations for now
				if int(row[rc_index]) > 0 and 'rect' in row[region_shape_attr]:
					#keep track of which file contributed which image and how many 
					#individual annotations the made and how many overall images they did
					if row[0] in file_contributions:
						file_contributions[row[0]] += 1
					else:
						file_contributions[row[0]] = 1
					#add the desired row to the combined list
					images_w_annotations.append(row)
			#append the file's contributions to the list of all contributions
			contributions.append((file, file_contributions))

	return header, images_w_annotations, contributions


def extract_useful(header, csv_annotations, path_to_images):
	"""
	this format is preffered by keras-retinanet
	the main program, it is a modified subset of the via output
	the basic form is file, x, y, x+w, y+h, class
	"""
	#locate the indexes of the data from the header
	filename_index = header.index('filename')
	region_shape_attr = header.index('region_shape_attributes')
	#region shape attributes are split up into 5 strings
	#the fifth one is the region attribute we want
	region_attr = region_shape_attr + 5

	new_annotations = []
	unique_classes = set()
	for row in csv_annotations:
		#@refactor:instead of hardcoding this make it an input param or at least a global
		new_row = [os.path.join(path_to_images, row[filename_index])]
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
		unique_classes.add(row[region_attr][start_of_name:-4])

		new_annotations.append(new_row)

	#this header describes the column it is above
	new_header = ['filename', 'TopL_x', 'TopL_y', 'BottomR_x', 'BottomR_y', 'class']
	return new_header, new_annotations, unique_classes

def printContributions(contributions):
	"""
	prints usefull information about how each file is contributing to 
	the final merged file
	"""
	for file, file_contributions in contributions:
			print('file {0} contributed {1} annotated pictures to the merged file'.format(
				file, len(file_contributions)))
			#sum up the individual annotations contriubted by each person
			individual_annotations = 0
			for annottation in file_contributions:
				individual_annotations += file_contributions[annottation]
			print('\ttotal annotations: {0}'.format(individual_annotations))
			print('\taverage annotations per file: {:.2f}\n'.format(
				individual_annotations / len(file_contributions)))

def main(path_to_files, type_of_files, path_to_images, save_to):
	"""
	this program combines multiple files of annotations
	generated by via, and it also prints out a report of 
	how the files contributed to the merged file
	via outputs 2 types of annotation files json and csv
	"""

	#@TODO: the json version of this program is out of date compared to the csv version
	if type_of_files == 'json':#merge json files
		annotations = combine_json_in_dir(path_to_files)

		annotations_as_json = json.dumps(annotations)
		#@refactor: right now I think we're just rewriting the entire file each time 
		#would it be worth it to make it only append? 
		with open(os.path.join(save_to, OUTPUT_JSON_FILENAME), 'w') as f:
			f.write(annotations_as_json)

		print('succesfully joined json files')
	elif type_of_files == 'csv':#merge csv files 
		header, annotations, contributions = combine_csv_in_dir(path_to_files)

		#change the form of the data to the one perfered by keras
		header, annotations, classes = extract_useful(header, annotations, path_to_images)
		#write out to the file as a csv 
		with open(os.path.join(save_to, OUTPUT_CSV_FILENAME), 'w') as outputcsv:
			#create the csv writter object 
			csv_writter = csv.writer(outputcsv, delimiter=',',
											quotechar = '|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			
			#write one row at a time first row is the header
			csv_writter.writerow(header)
			for row in annotations:
				csv_writter.writerow(row)

		with open(os.path.join(save_to, CLASSES_CSV_FILENAME), 'w') as classescsv:
			csv_class_writter = csv.writer(classescsv, delimiter=',', quotechar = '|',
																 quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			for i, annotation_class in enumerate(classes):
				csv_class_writter.writerow([annotation_class, i])

		#print success and output statistics 
		print('succesfully joined csv files')
		printContributions(contributions)

if __name__ == '__main__':
	#make sure all necessary arguments are passed into the program
	#need a path to where the files are, and which type of file csv or json
	#and optionally the directory which contains the images
	parser = argparse.ArgumentParser()
	parser.add_argument('path_to_files', metavar='PTF')
	parser.add_argument('type_of_files', choices=['json', 'csv'])
	parser.add_argument('--path_to_images', '-pti', default='//home//ayeshag//ImageDump//')
	parser.add_argument('--save_to', '-st', default=sys.argv[1])
	
	parsed = parser.parse_args(sys.argv[1:]) 
	main(parsed.path_to_files, parsed.type_of_files, parsed.path_to_images, parsed.save_to)
