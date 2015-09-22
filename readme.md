pyCatalog
=========

Obviously this is a work in progress.

Objective: to have a catalog of my media collection (CDs, DVDs, Blurays, books, etc.) as well as,
possibly, other things I might want to inventory. Amazon is the primary data aggregation backend
and the search UI is tuned to support new item entry using my Bluetooth barcode scanner. I don't
expect that this will ever become a full-fledged library exploration tool; for me, the main purpose
is getting a populated DB.

## Requirements

Links go to library homepage, otherwise the Ubuntu package name is given in parens.

* [json-rpc](https://pypi.python.org/pypi/json-rpc/)
* SQLAlchemy (python-sqlalchemy)
* Tornado (python-tornado)

You'll also need:

* An Amazon Advertising API key pair. You can sign up on
  [Amazon's site](https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html).

## Setup

1. Copy `config.py.example` to `config.py`
2. Edit `config.py` to include your Amazon key details
3. To build the SQL database, run `./build_db.py`. You'll need to edit the script to remove the
   startup warning, which exists so that I don't accidentally run it and delete my database.
4. Run `./pyCatalog.py`. Observe that there are no startup errors.
5. Visit http://localhost:8000/new.html to begin adding items.

## Adding items

### Using a barcode scanner for rapid entry

1. Click inside the UPC/EAN box
2. Scan your barcode. The scanner should terminate with an Enter keypress.
3. When a result appears (assuming it does), you can observe its details at the bottom. If there
   is an error with the barcode, the box will turn red. This usually means there was no result.
4. Check the auto-add box at the bottom and return to select the UPC code textbox.
5. Repeat as necessary. Each new scan will cause the previous entry to be saved.

### Manually

1. Search in any of the text boxes
2. For searches with multiple results, select the result you want to keep.
3. If you have trouble finding results using the keyword feature, I find it works best to use
   Amazon's website to find the appropriate item, then enter the ASIN (which looks like B003Y5H5HY)
   and enter it directly into the ASIN box.
4. Click the `Add Item` button

Each time you add an item, a toast should appear in the top right to indicate whether the action
was successful. Duplicate items are skipped automatically (as per their ASIN).
