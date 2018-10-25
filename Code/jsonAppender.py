import os
import json
from os import listdir
from os.path import isfile, join

'''
Appends one .json file to another .json file
for use in congregating the annotated .json files together
'''

def cat_json(output_filename, input_filenames):
    with open(output_filename, "w") as outfile:
        firstFile = True
        for infile_name in input_filenames:
            with open(infile_name) as infile:
                if firstFile:
                    outfile.write('[')
                    firstFile = False
                else:
                    outfile.write(',')
                outfile.write(mangle(infile.read()))
        outfile.write(']')

def mangle(s):
    return s.strip()[1:-1] #start:end possibly need to change

def combine_annotations_in_dir(directory):
	images_w_annotations = {}
	for file in os.listdir(directory):
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

def main():
	mypath = os.getcwd()
	#input_files = [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
	path_to_json = os.path.join('..', 'annotations')
	annotations = combine_annotations_in_dir(path_to_json)
	print(annotations)	

		#images_w_annotations.sort()
	print(annotations)


if __name__ == '__main__':
    main()