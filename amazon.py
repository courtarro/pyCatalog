
import bottlenose

# Local imports
import xml_fix
from config import *
from model import *
from utils import *

amazon_cache = {}


class Amazon(object):

    def __init__(self):
        self.amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)

    def search(self, keywords):
        # Perform Query by UPC or Other String
        # This process will search for items on Amazon using a set of keywords or a UPC

        # sample keyword (upc): '851147006055'
        response = self.amazon.ItemSearch(Keywords=keywords, SearchIndex='All')
        with open('debug.txt', 'w') as debug_file:
            debug_file.write(response)
        res_x = xml_fix.fromstring(response)
        success = res_x.find('Items/Request/IsValid').text == 'True'
        if success:
            items_x = res_x.findall('Items/Item')
            items = []
            for item_x in items_x:
                items.append(self._xml_to_dict(item_x))
            return items
        else:
            return None

    def lookup(self, item_id, id_type='ASIN', return_xml=False):
        # Perform Query by single-item ID (assumes only one matching item, default type is ASIN)

        # sample ASIN: 'B00LOWJ6JY'
        print item_id, id_type
        if id_type == 'ASIN':
            response = self.amazon.ItemLookup(ItemId=item_id, IdType=id_type)
        else:
            response = self.amazon.ItemLookup(ItemId=item_id, IdType=id_type, SearchIndex='All')
        with open('debug.txt', 'w') as debug_file:
            debug_file.write(response)
        res_x = xml_fix.fromstring(response)
        success = res_x.find('Items/Request/IsValid').text == 'True'
        if success:
            item_x = res_x.find('Items/Item')
            if return_xml:
                return item_x
            else:
                return self._xml_to_dict(item_x)
        else:
            return None

    def lookup_with_cache(self, asin, return_xml=False):
        if amazon_cache.has_key(asin):
            print "Cache hit."
            if return_xml:
                return amazon_cache[asin]
            else:
                return self._xml_to_dict(amazon_cache[asin])
        else:
            print "Cache miss."
            item_x = self.lookup(asin, 'ASIN', return_xml=True)
            amazon_cache[asin] = item_x                       # cache the raw XML object
            if return_xml:
                return item_x
            else:
                return self._xml_to_dict(item_x)

    def to_item(self, amazon_item):
        # Convert from Amazon Item to Media Item

        asin = amazon_item.find('ASIN').text
        item_attr = amazon_item.find('ItemAttributes')
        group = item_attr.find('ProductGroup').text

        if group == 'DVD':
            new_item = Movie()
            new_item.title = item_attr.find('Title').text
            director = item_attr.find('Director')
            if director is not None:
                new_item.director = director.text

            actor = item_attr.find('Actor')
            if actor is not None:
                new_item.actor = actor.text

            manufacturer = item_attr.find('Manufacturer')
            if manufacturer is not None:
                new_item.publisher = manufacturer.text
        elif group == 'Music':
            new_item = Music()
            new_item.title = item_attr.find('Title').text
            if item_attr.find('Artist') is not None:
                new_item.artist = item_attr.find('Artist').text
            elif item_attr.find("Creator[@Role='Composer']") is not None:
                new_item.artist = item_attr.find("Creator[@Role='Composer']").text

            manufacturer = item_attr.find('Manufacturer')
            if manufacturer is not None:
                new_item.label = manufacturer.text
        else:
            new_item = Item()
            print 'Warning: unknown product group: ' + group

        new_item.external_ids.append(ExternalId(provider=ExternalIdProvider.Amazon, external_id=asin))

        return asin, new_item

    def add_images_to_item(self, item, asin):
        covers_a = self.get_item_imagesets(asin)
        if (covers_a is not None) and len(covers_a):
            for img_type, cover_a in covers_a.iteritems():
                url = self.get_best_image_url(cover_a)
                filename = fetch_image(url)
                if filename:
                    img = Image(type=img_type, filename=filename)
                    item.images.append(img)
        return

    def get_item_imagesets(self, asin):
        response = self.amazon.ItemLookup(ItemId=asin, ResponseGroup='Images')
        res_x = xml_fix.fromstring(response)
        success = res_x.find('Items/Request/IsValid').text == 'True'
        if success:
            covers_x = {}
            image_x = res_x.find('Items/Item/ImageSets')
            if (image_x is not None) and len(image_x):
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

    def get_item_image_url(self, asin):
        imagesets_x = self.get_item_imagesets(asin)
        if imagesets_x:
            return self.get_best_image_url(imagesets_x[ImageType.FrontCover])
        else:
            return None

    # --- Private methods ---
    def _xml_to_dict(self, item_x):
        if item_x is None:
            return None

        asin = item_x.find('ASIN').text

        item = {'asin': asin}
        att = item_x.find('ItemAttributes')
        title = att.find('Title')
        if title is not None: item['title'] = title.text
        group = att.find('ProductGroup')
        if group is not None: item['group'] = group.text
        actor = att.find('Actor')
        if actor is not None: item['actor'] = actor.text
        manufacturer = att.find('Manufacturer')
        if manufacturer is not None: item['manufacturer'] = manufacturer.text
        director = att.find('Director')
        if director is not None: item['director'] = director.text

        # If there's not an artist but there IS a composer, use the composer as the artist
        artist = att.find('Artist')
        if artist is None:
            composer = att.find("Creator[@Role='Composer']")
            if composer is not None:
                item['artist'] = composer.text
        else:
            item['artist'] = artist.text

        return item