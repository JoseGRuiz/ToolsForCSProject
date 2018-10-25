import os
import json

OUTPUT_JSON_FILENAME = 'annotations_group.json'

'''
combines the json files in a given directory
for now assuming the directory contains only json files
returns a dictionary with all annotations merged 
'''
def combine_annotations_in_dir(directory):
	images_w_annotations = {}
	for file in os.listdir(directory):
		if file == OUTPUT_JSON_FILENAME: #skip the merged file
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

def main():
	path_to_json = os.path.join('..', 'annotations')
	annotations = combine_annotations_in_dir(path_to_json)

	print(annotations)
	annotations_as_json = json.dumps(annotations)
	#right now I think we're just rewriting the entire file each time 
	#would it be worth it to make it only append? 
	with open(os.path.join(path_to_json, OUTPUT_JSON_FILENAME), 'w') as f:
		f.write(annotations_as_json)

if __name__ == '__main__':
    main()