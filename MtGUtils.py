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
    return next(card for card in Card.where(name = name).all() if card.image_url is not None)


class Deck:

    # Colors of the cards don't change, so we make this a class variable
    color_ids = 'B', 'U', 'G', 'R', 'W', None

    def __init__(self, cards = () ):
        self.cards = [get_card_by_name(card) for card in cards]

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
    def manaColorProportions(self):
        colors = [card.color_identity[0] for card in self.cards]
        counts = [colors.count(id) for id in Deck.color_ids]
        proportions = [count/len(colors) for count in counts]
        return proportions

    @property
    def mana_curve(self):
        pass

    @property
    def total_power(self):
        pass

    def card_type_proportions(self):
        pass

    def average_creature_power(self):
        pass

    def get_card(self, cardName):
        return next(card for card in self.cards if card.name == cardName)

    def add_card(self, card):
        """Should be called with a string or a Card object"""
        #self.cards.append(card) if type(card) == Card else self.cards.append(get_card_by_name(card))
        self.cards.append(card) if type(card) is Card else self.cards.append(get_card_by_name(card))

    @staticmethod
    def search(cardStr):
        #TODO optimize this because I am creating card objects twice
        #I think it may be better optimized now but it's ugly as all hell
        results = Card.where(name=cardStr).all()
        cardNames = set(card.name for card in results)
        deck = Deck()
        for cardname in cardNames:
            for card in results:
                if card.name == cardname and card.image_url is not None:
                    deck.add_card(card)
                    break
                continue
        return deck







a = Deck(["LLanowar Elves", "Swords to plowshares"])

print(a)