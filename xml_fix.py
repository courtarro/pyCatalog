from StringIO import StringIO
import xml.etree.ElementTree as ETree

__author__ = 'Ethan Trewhitt'


def fromstring(xml):
    # instead of ET.fromstring(xml)
    it = ETree.iterparse(StringIO(xml))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
    root = it.root
    return root