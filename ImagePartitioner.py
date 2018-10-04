import os
import csv
from random import shuffle

def main():
	students = ['Logan Padon', 'Ayan Paul', 'Ayesha Gurnani',
						'Divyesh', 'Jose Ruiz', 'Kenny Hoang', 'Rutuja Kaushike', 'Victor']
	file_names = os.listdir('ImageURLs')

	URLs = []
	for file_name in file_names:
		if '.csv' in file_name: #only interested in csv files
			URLs.extend(read_links(os.path.join('ImageURLs', file_name)))

	#how many should each student worry about 
	per_student = len(URLs)/len(students)
	per_student = int(per_student)	#lazy floor

	#add some randomness
	shuffle(URLs)

	#create a dictionary with student names as keys 
	#and slices of the URL list as the URLs they will work with
	start = 0
	end = per_student 
	responsibilities = {}
	for student in students:
		responsibilities[student] = URLs[start:end]
		start = end
		end += per_student

		#create and write the assignmets for each student
		for k in responsibilities:
			with open(os.path.join('assignments', k + '.txt'), 'w') as f:
				for url in responsibilities[k]:
					f.write(url + '\n')



#read in links for a given file
def read_links(file):
	with open(file) as csv_file:
		reader = csv.reader(csv_file, delimiter = ",")

		links = [t[0] for t in reader if "https://" in t[0]]
	return links

if __name__ == '__main__':
	main()
