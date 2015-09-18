import urllib2
import uuid

from config import *


def fetch_image(image_url):
    image = urllib2.urlopen(image_url).read()
    new_filename = str(uuid.uuid4()) + '.jpg'
    with open(IMAGES_PATH + "/" + new_filename, 'wb') as image_file:
        image_file.write(image)

    return new_filename
