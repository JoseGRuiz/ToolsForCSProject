import os
import sys
import csv
from random import shuffle
from zipfile import ZipFile

'''
splits files up between people, specifically those in our 
group first it was link distribution now it is image file 
distribution and compression to zip files
'''
def main():
	students = ['Logan Padon', 'Ayan Paul', 'Ayesha Gurnani',
						'Divyesh Patel', 'Jose Ruiz', 'Kenny Hoang', 'Rutuja Kaushike', 'Victor Dang']
	file_name = 'ImageDump.zip'
	if len(sys.argv) > 1:
		force_dump = bool(sys.argv[1])
	else: 
		force_dump = False

	with ZipFile(file_name, 'r') as zip:
		picture_names = os.listdir('ImageDump')
		if force_dump or len(picture_names) != len(zip.namelist()):
			zip.extractall()

	picture_names = os.listdir('ImageDump')

	#how many should each student worry about 
	per_student = len(picture_names)/len(students)
	per_student = int(per_student)	#lazy floor

	#add some randomness
	shuffle(picture_names)

	#create a dictionary with student names as keys 
	#and slices of the URL list as the URLs they will work with
	start = 0
	end = per_student 
	responsibilities = {}
	for student in students:
		responsibilities[student] = picture_names[start:end]
		start = end
		end += per_student

	os.makedirs('Images_compressed', exist_ok = True)
	#create and write the assignmets for each student
	for k in responsibilities:
		write_files_to_zip(os.path.join('Images_Compressed', k + '.zip'),
										'ImageDump', responsibilities[k])

	print('files zipped succesfully!')

#read in links for a given file
def read_links(file):
	with open(file) as csv_file:
		reader = csv.reader(csv_file, delimiter = ",")

		links = [t[0] for t in reader if "https://" in t[0]]
	return links

#write files to a zip file, given a path and a list of files
def write_files_to_zip(path_to_write, path_to_read, files):
	with ZipFile(path_to_write, 'w') as zip:
		for file in files:
			zip.write(os.path.join(path_to_read, file))

if __name__ == '__main__':
	main()
