from mtgsdk import Card
from mtgsdk import QueryBuilder
from mtgsdk.restclient import RestClient
from mtgsdk.config import __endpoint__
import collections




def get_card_by_name(name):
    """ This takes in a card name, and returns a single card object.
        When using the API, a search for a single card by name returns an object of the card for every set it was printed in.
        This is to get around that.
        :param name: Name of the card to search
        :returns: Card object
        """
    return next(card for card in Card.where(name = name) if card.image_url is not None)

def search(**kwargs):
    """This is to be used to search the api for a card by ambiguous parameters and return a deck container with the resulting cards
        I think I am going to update it to contain a dictionary that maps the keys and values to the filters used. It does now."""
    results = Card.where(**kwargs).all()
    cardNames = set(card.name for card in results)
    return Deck([next(card for card in results if card.name == name and card.image_url is not None) for name in cardNames])


    """
    for cardname in cardNames:
        for card in results:
            if card.name == cardname and card.image_url is not None:
                deck.add_card(card)
                break
            continue

            """


class Deck(collections.MutableSequence):
    # Colors of the cards don't change, so we make this a class variable
    color_ids = 'B', 'U', 'G', 'R', 'W', None

    def __init__(self, cards = [] ):
        """A deck can be initialized with no parameters, with a list of strings, or a list of card objects."""
        self.cards = [get_card_by_name(card) for card in cards] if cards and type(cards[0]) is str else cards

    def __iter__(self):
        for card in self.cards:
            yield card

    def __str__(self):
        return '\n'.join([card.name for card in self])

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, index):
        return self.cards[index]

    def __delitem__(self, index):
        del(self.cards[index])

    def __setitem__(self, key, value):
        self.cards[key] = value if type(value) is Card else get_card_by_name(value)

    def insert(self, index, value):
        self.cards.insert(index,value)

    def get_card(self, cardNameStr):
        return next(card for card in self.cards if card.name == cardNameStr)

    def add_card(self, card):
        """Should be called with a string or a Card object"""
        #self.cards.append(card) if type(card) == Card else self.cards.append(get_card_by_name(card))
        self.cards.append(card) if type(card) is Card else self.cards.append(get_card_by_name(card))


    @property
    def mean_mana(self):
        return sum([card.cmc for card in self])/len(self)


    @property
    def mana_curve_tuple(self):
        maxr = range(max(card.cmc for card in self))
        return []

    @property
    def manaColorProportions(self):
        for card in self.cards:
            print(card.mana_cost)
            print(card.type)

        #I'm sure this area could be chopped down
        colors = [card.color_identity[0] if type(card.color_identity) is type([]) else None for card in self.cards]
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





a = Deck(["LLanowar Elves", "Swords to plowshares"])

print(a)