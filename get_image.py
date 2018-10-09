
import os
import csv
import urllib.request
from PIL import Image

# change constants as needed
IMAGE_URL_FOLDER = "ImageURLs/" # this folder will hold the files that has the URLs
IMAGE_DUMP_FOLDER = "ImageDump/" # this folder is where the pictures will be saved to
IMAGE_SIZE = (500,500) # final size of the images


# Added image resizing in this function
def get_image(url, image_path, size = IMAGE_SIZE):
    urllib.request.urlretrieve(url, image_path)
    image = Image.open(image_path)
    image = image.resize(IMAGE_SIZE)
    image.save(image_path)


# seems pointless for now
def read_txt(file_location, filename):
    with open(file_location + filename) as txt_file:
        i = 0

        for line in txt_file:
            if "https://" in line:
                # grabs only the URL from the line in the text file and removes the leading whitespaces
                url = line.split(" : ")[0].replace("\"", "").lstrip()
                get_image(url, IMAGE_DUMP_FOLDER + str(i) + ".jpg")
                i += 1


# grab only the links from the csv files
def read_csv(file_location, filename):
    with open(file_location + filename) as csv_file:
        i = 0
        reader = csv.reader(csv_file, delimiter = ",")

        for line in reader:
            if "https://" in line[0]:
                get_image(line[0], IMAGE_DUMP_FOLDER + str(i) + ".jpg")
                i += 1


if __name__ == "__main__":
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
