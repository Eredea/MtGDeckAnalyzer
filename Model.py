from mtgsdk import Card
from mtgsdk import Set
from mtgsdk import Type
from mtgsdk import Supertype
from mtgsdk import Subtype
from mtgsdk import Changelog
import wget
from PIL import Image, ImageTk


def get_card_by_name(name):
    """ This takes in a card name, and returns a single card object.
        When using the API, a search for a single card by name returns an object of the card for every set it was printed in.
        This is to get around that.
        :param name: Name of the card to search
        :returns: Card object
        """
    cards = Card.where(name = name).all()
    for card in cards:
        if card.image_url is not None:
            return card

def get_card_picture(name):
    """:param name: string of card's name
       :returns ImageTk.PhotoImage of
    """
    cards = Card.where(name = name).all()
    for card in cards:
        if card.image_url is not None:
            imageLoc = "{}.png".format(name)
            wget.download(card.image_url, out=imageLoc)
            imageObj = ImageTk.PhotoImage(Image.open(imageLoc))
            # Here I also learned all about the break statement, including that it wasn't necessary.
            return imageObj

class Deck:

    def __init__(self):
        self.cards = []
    pass

