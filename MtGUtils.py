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

def get_card_picure(name):
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

    # Colors of the cards don't change, so we make this a class variable
    color_ids = 'B', 'U', 'G', 'R', 'W', None

    def __init__(self, cards = () ):
        self.cards = [get_card_by_name(card) for card in cards]
    pass

    def __iter__(self):
        for card in self.cards:
            yield card

    def __str__(self):
        return '\n'.join([card.name for card in self])

    @property
    def mean_mana(self):
        return sum([card.cmc for card in self.cards])/len(self.cards)

    @property
    def mana_curve_tuple(self):
        return []

    @property
    def mana_curve_proportions(self):

        colors = [card.color_identity[0] for card in self.cards]
        counts = [colors.count(id) for id in Deck.color_ids]
        proportions = [count/len(colors) for count in counts]
        return proportions


    def add_card(self, card):
        """Should be called with a string or a Card object"""
        self.cards.append(card) if type(card) is Card else self.cards.append(get_card_by_name(card))


a = Deck(["LLanowar Elves", "Swords to plowshares"])

print(a)