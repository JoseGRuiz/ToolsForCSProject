import os
import sys
import csv
from random import shuffle
from zipfile import ZipFile


def main():
	"""
	splits files up between people, specifically those in our 
	group first it was link distribution now it is image files 
	distribution and compression to zip files
	"""
	#list of students involved in the project
	#@TODO: make this be read from a file or somehow more dynamic 
	students = ['Logan Padon', 'Ayan Paul', 'Ayesha Gurnani',
						'Divyesh Patel', 'Jose Ruiz', 'Kenny Hoang', 'Rutuja Kaushike', 'Victor Dang']
	#give a zip file containing all Images to the program
	#this assumes that the script and zip file are in the same directory
	#@TODO: this could also be an argument to the program
	file_name = 'ImageDump.zip'

	#force_dump is a program argument that if passed in as true
	#will force the zipfile to be read, prevents unnecessary unzipping
	if len(sys.argv) > 1:
		force_dump = bool(sys.argv[1])
	else: 
		force_dump = False

	picture_names = os.listdir('ImageDump')
	with ZipFile(file_name, 'r') as zip:
		#only exctract from  the zip file if not all pictures are yet in 
		#the directory or if forced to 
		if force_dump or len(picture_names) != len(zip.namelist()):
			zip.extractall()

	#divide the number of pictures by the ammount of students
	#and calculate how many each student should be responsible for
	per_student = len(picture_names)/len(students)
	per_student = int(per_student)	#@refactor: lazy floor

	#add some randomness to reduce probability that someone gets only 
	#bad images or someone gets an unfair ammount of work 
	shuffle(picture_names)

	#create a dictionary with student names as keys 
	#and slices of the image list as the images they will work with
	start = 0
	end = per_student 
	responsibilities = {}
	#give each student the same amount of work, next slice starts 
	#where the last slice ends 
	for student in students:
		#take a slice of the total list as the student's list
		responsibilities[student] = picture_names[start:end]
		#update start and end to mark the next slice
		start = end
		end += per_student

	#make the directory if it doesn't exit
	os.makedirs('Images_compressed', exist_ok = True)
	#for the student's list of responsibilities zip their assignments
	#into a zip file file is named the same as the student
	for k in responsibilities:
		write_files_to_zip(os.path.join('Images_Compressed', k + '.zip'),
										'ImageDump', responsibilities[k])

	print('files zipped succesfully!')

def read_links(file):
	"""
	read in urls for a given csv file
	this function no longer serves a purpose in the current
	implementation but it might be usefull later

	Args:
	file: the file to read the links from
	"""

	#open the file as a csv
	with open(file) as csv_file:
		reader = csv.reader(csv_file, delimiter = ",")

		#assume that the urls are the first value in the csv
		links = [t[0] for t in reader if "https://" in t[0]]
	
	return links

def write_files_to_zip(path_to_write, path_to_read, files):
	"""
	writes files to a zip file

	Args: 
	path _to_write: where to save the file to 
	path_to_read: the path were the files to be zipped are
	files: a list of files 
	"""
	with ZipFile(path_to_write, 'w') as zip:
		for file in files:
			zip.write(os.path.join(path_to_read, file))

if __name__ == '__main__':
	main()
