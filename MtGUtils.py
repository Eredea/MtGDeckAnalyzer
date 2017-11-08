from mtgsdk import Card
from Deck import Deck
from PIL import Image, ImageTk
from urllib.request import urlopen
from io import BytesIO
# Have another circular dependency from deck and MtGUtils
"""Provides an interface to the MtG SdK library to search cards. 
Uses self-created Deck class as a container for card objects"""


def get_card_by_name(name):
    """ DONE
    This takes in a card name, and returns a single card object.
        When using the API, a search for a single card by name returns an object of the card for every set it was printed in.
        This is to get around that.
        :param name: Name of the card to search
        :returns: Card object
        """
    return next(card for card in Card.where(name = name) if card.image_url is not None)


def search(**kwargs):
    results = Card.where(**kwargs).all()
    cardNames = set(card.name for card in results)
    return Deck([next(card for card in results if card.name == name and card.image_url is not None) for name in cardNames])


def get_card_picture(card):
    """:param card: Card object
       :returns ImageTk.PhotoImage of Card
    """
    # We ultimately create an Image object after downloading from a url, reading the raw data with a context manager
    # and recreating it from its bytes
    with urlopen(card.image_url) as f:
        with Image.open(BytesIO(f.read())) as imageFile:
            return ImageTk.PhotoImage(imageFile)
    return None