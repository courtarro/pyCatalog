#!/usr/bin/env python

import bottlenose
import sqlite3
import sys
import urllib2
import uuid

# Local imports
import xml_fix
from config import *
from constants import *

# Amazon Searches
amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)


def amazon_search(keywords):
    # Perform Query by UPC or Other String
    # This process will search for items on Amazon using a set of keywords or a UPC
    
    # sample keyword (upc): '851147006055'
    response = amazon.ItemSearch(Keywords=keywords, SearchIndex='All')
    res_x = xml_fix.fromstring(response)
    success = res_x.find('Items/Request/IsValid').text == 'True'
    if success:
        item_x = res_x.find('Items')
        return item_x.findall('Item')
    else:
        return None


def amazon_lookup(asin):
    # Perform Query by ASIN (assumes only one matching item)

    # sample ASIN: 'B00LOWJ6JY'
    response = amazon.ItemLookup(ItemId=asin)
    res_x = xml_fix.fromstring(response)
    success = res_x.find('Items/Request/IsValid').text == 'True'
    if success:
        item_x = res_x.find('Items/Item')
        return item_x
    else:
        return None


def amazon_to_item(item_x, upc=None):
    # Convert from Amazon Item to Media Item
    
    asin = item_x.find('ASIN').text
    item_attr = item_x.find('ItemAttributes')
    group = item_attr.find('ProductGroup').text

    new_item = {}
    new_item['external_ids'] = {}
    new_item['external_ids'][ExternalIdProvider.Amazon] = asin
    if upc is not None:
        new_item['external_ids'][ExternalIdProvider.UPC] = upc
        
    if group == 'DVD':
        new_item['type'] = MediaType.Movie
        new_item['title'] = item_attr.find('Title').text
        new_item['director'] = item_attr.find('Director').text
        new_item['actor'] = item_attr.find('Actor').text
        new_item['publisher'] = item_attr.find('Manufacturer').text
    elif group == 'Music':
        new_item['type'] = MediaType.Music
        new_item['title'] = item_attr.find('Title').text
        new_item['artist'] = item_attr.find('Artist').text
        new_item['label'] = item_attr.find('Manufacturer').text
    else:
        print 'Unknown product group: ' + group

    return asin, new_item


def amazon_fetch_image(imageset_x):
    # Fetch Images from Amazon
    if imageset_x is None:
        return None

    max_size = max_img = None
    
    for img_x in imageset_x:
        width = int(img_x.find('Width').text)
        height = int(img_x.find('Height').text)
        size = width * height
        if (max_size is None) or (size > max_size):
            max_size = size
            max_img = img_x.find('URL').text
            
    if max_img is None:
        return None
    
    image = urllib2.urlopen(max_img).read()
    new_filename = str(uuid.uuid4()) + '.jpg'
    with open(IMAGES_PATH + "/" + new_filename, 'wb') as image_file:
        image_file.write(image)
        
    return new_filename


def amazon_fetch_images(asin):
    response = amazon.ItemLookup(ItemId=asin, ResponseGroup='Images')
    res_x = xml_fix.fromstring(response)
    success = res_x.find('Items/Request/IsValid').text == 'True'
    if success:
        covers = {}
        image_x = res_x.find('Items/Item/ImageSets')
        if len(image_x):
            front_filename = fetch_image(image_x.find("ImageSet[@Category='primary']"))
            if front_filename is not None:
                covers[CoverType.Front] = front_filename
            back_filename = fetch_image(image_x.find("ImageSet[@Category='variant']"))
            if back_filename is not None:
                covers[CoverType.Back] = back_filename
        return covers
    else:
        return None


def write_new_item(new_item):
    # Write New Item to Database
    con = sqlite3.connect(CATALOG_DB)
    cur = con.cursor()

    # Main item ID
    cur.execute('insert into item default values;')
    item_id = cur.lastrowid

    # External IDs
    for provider, eid in new_item['external_ids'].iteritems():
        params = (item_id, provider, eid)
        cur.execute('insert into external_id (item_id, provider, external_id) values (?,?,?)', params)
        
    # Extra details
    if new_item['type'] == MediaType.Movie:
        params = (item_id, new_item['title'], new_item['actor'], new_item['director'], new_item['publisher'])
        cur.execute('insert into movie (item_id, title, actor, director, publisher) values (?,?,?,?,?)', params)
    elif new_item['type'] == MediaType.Music:
        params = (item_id, new_item['title'], new_item['artist'], new_item['label'])
        cur.execute('insert into music (item_id, title, artist, label) values (?,?,?,?)', params)
        
    # Images
    for image_type, filename in new_item['covers'].iteritems():
        params = (item_id, image_type, filename)
        cur.execute('insert into image (item_id, type, filename) values (?,?,?)', params)

    con.commit()
    con.close()
    
    return item_id


def test_amazon_query():
    upc = '851147006055'
    items_a = amazon_search(upc)
    if (items_a is None) or (not len(items_a)):
        sys.exit("No item with that UPC")
    item_a = items_a[0]
    asin, item = amazon_to_item(item_a, upc)
    covers = fetch_images(asin)
    if (covers is not None) and len(covers):
        item['covers'] = covers
    write_new_item(item)


if __name__ == '__main__':
    test_query()