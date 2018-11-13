
import os
import os.path
import csv
import urllib.request
from PIL import Image


'''
Change these fields as needed. 
The folder paths below are relative paths, change them to absolute paths if needed.
'''

# this folder will hold the files that has the URLs, this folder is required to be 
# created beforehand and have the files already inside
IMAGE_URL_FOLDER = "ImageURLs/" 

# this folder is where the pictures will be saved to, note that this folder
# does not need to exist beforehand
IMAGE_DUMP_FOLDER = "ImageDump/" 

# final size of the images
IMAGE_SIZE = (500,500) 


# the value in which the images will be renamed to, recommended not to be touched
index = 0


def get_image(url, image_path, size = IMAGE_SIZE):
    '''
    Grabs an image from the provided url and saves the image to the specified folder.
    This function will also resize the image to the size specified by the IMAGE_SIZE field.
    This function is called from either the read_text() or read_csv() functions.


    Parameters
    ----------
    url : string
        The url to grab the image from
    image_path : string
        The path to the save the picture to
    image_size : list 
        The desired size of the images, can be changed by changin the value of IMAGE_SIZE field 
        or passing desired image size whenever calling this function
    '''


    # if statement added here so that if the program stops (which is does for whatever reason),
    # the program can be executed again and will resume from where it stopped
    if not os.path.isfile(image_path):
        urllib.request.urlretrieve(url, image_path)
        image = Image.open(image_path)
        image = image.resize(IMAGE_SIZE)
        image.save(image_path)


def read_txt(file_location, filename):
    '''
    Grabs url's from a specified text file, however this should be modified to grab url's from a text file
    since this function was written to extract a url from a particular formatted text file provided by the 
    sponsor.


    Parameters
    ----------
    file_location : string
        The path where the image is located in
    filename : string
        The name of the file that will be used to grab the url's from
    '''

    global index 

    with open(file_location + filename) as txt_file:
        for line in txt_file:
            if "https://" in line:
                # grabs only the URL from the line in the text file and removes the leading whitespaces
                url = line.split(" : ")[0].replace("\"", "").lstrip()
                get_image(url, IMAGE_DUMP_FOLDER + str(index) + ".jpg")
                index += 1
                

def read_csv(file_location, filename):
    '''
    Grabs the url's from a csv file. Modify as needed since this grabs a url from a particuarly formatted
    csv file.


    Parameters
    ----------
    file_location : string
        The path where the image is located in
    filename : string
        The name of the file that will be used to grab the url's from
    '''

    global index 

    with open(file_location + filename) as csv_file:
        reader = csv.reader(csv_file, delimiter = ",")

        # grab only the url's after splitting the values
        for url in reader:
            if "https://" in url[0]:
                get_image(url[0], IMAGE_DUMP_FOLDER + str(index) + ".jpg")
                index += 1


def main():
    '''
    This script will grab url's from the files provided, resize them to a desired
    size and save them to a specified folder. The folder to grab the files from, save to
    and the size of the images are fields located at the top of the script.

    NOTICE: For reasons unknown, this program stops executing after grabbing a certain 
    amount of pictures. A simple workaround is just to simply run the script again whenever 
    it stops. The script will resume from where it stopped after the previous execution.
    '''

    # this folder needs to be created beforehand with 
    # the files already inside
    files = os.listdir(IMAGE_URL_FOLDER)

    # creates a folder to dump all of the images in
    # if it doesn't already exist
    os.makedirs(IMAGE_DUMP_FOLDER, exist_ok = True)

    for f in files:
        if ".txt" in f:
            read_txt(IMAGE_URL_FOLDER, f)
        elif ".csv" in f:
            read_csv(IMAGE_URL_FOLDER, f)


if __name__ == '__main__':
    main()
