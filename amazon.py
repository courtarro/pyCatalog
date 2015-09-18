
import bottlenose

# Local imports
import xml_fix
from config import *
from model import *


class Amazon(object):

    def __init__(self):
        self.amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)

    def search(self, keywords):
        # Perform Query by UPC or Other String
        # This process will search for items on Amazon using a set of keywords or a UPC

        # sample keyword (upc): '851147006055'
        response = self.amazon.ItemSearch(Keywords=keywords, SearchIndex='All')
        res_x = xml_fix.fromstring(response)
        success = res_x.find('Items/Request/IsValid').text == 'True'
        if success:
            item_x = res_x.find('Items')
            return item_x.findall('Item')
        else:
            return None

    def lookup(self, asin):
        # Perform Query by ASIN (assumes only one matching item)

        # sample ASIN: 'B00LOWJ6JY'
        response = self.amazon.ItemLookup(ItemId=asin)
        res_x = xml_fix.fromstring(response)
        success = res_x.find('Items/Request/IsValid').text == 'True'
        if success:
            item_x = res_x.find('Items/Item')
            return item_x
        else:
            return None

    def to_item(self, amazon_item, upc=None):
        # Convert from Amazon Item to Media Item

        asin = amazon_item.find('ASIN').text
        item_attr = amazon_item.find('ItemAttributes')
        group = item_attr.find('ProductGroup').text

        if group == 'DVD':
            new_item = Movie()
            new_item.title = item_attr.find('Title').text
            new_item.director = item_attr.find('Director').text
            new_item.actor = item_attr.find('Actor').text
            new_item.publisher = item_attr.find('Manufacturer').text
        elif group == 'Music':
            new_item = Music()
            new_item.title = item_attr.find('Title').text
            new_item.artist = item_attr.find('Artist').text
            new_item.label = item_attr.find('Manufacturer').text
        else:
            new_item = Item()
            print 'Warning: unknown product group: ' + group

        new_item.external_ids.append(ExternalId(provider=ExternalIdProvider.Amazon, external_id=asin))
        if upc is not None:
            new_item.external_ids.append(ExternalId(provider=ExternalIdProvider.UPC, external_id=upc))

        return asin, new_item

    def get_imagesets(self, asin):
        response = self.amazon.ItemLookup(ItemId=asin, ResponseGroup='Images')
        res_x = xml_fix.fromstring(response)
        success = res_x.find('Items/Request/IsValid').text == 'True'
        if success:
            covers_x = {}
            image_x = res_x.find('Items/Item/ImageSets')
            if len(image_x):
                front_x = image_x.find("ImageSet[@Category='primary']")
                if front_x is not None:
                    covers_x[ImageType.FrontCover] = front_x
                back_x = image_x.find("ImageSet[@Category='variant']")
                if back_x is not None:
                    covers_x[ImageType.BackCover] = back_x
            return covers_x
        else:
            return None

    def get_best_image_url(self, imageset_x):
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

        return max_img
