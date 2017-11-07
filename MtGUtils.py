from mtgsdk import Card
import collections

def get_card_by_name(name):
    """ This takes in a card name, and returns a single card object.
        When using the API, a search for a single card by name returns an object of the card for every set it was printed in.
        This is to get around that.
        :param name: Name of the card to search
        :returns: Card object
        """
    return next(card for card in Card.where(name = name) if card.image_url is not None)

def search(cardStr):
    """This is to be used to search the api for a card by ambiguous parameters and return a deck container with the resulting cards
        I think I am going to update it to contain a dictionary that maps the keys and values to the filters used."""
    results = Card.where(name=cardStr, ).all()
    cardNames = set(card.name for card in results)
    cardList = [next(card for card in results if card.name == name and card.image_url is not None) for name in cardNames]

    deck = Deck(cardList)
    return deck






    """
    for cardname in cardNames:
        for card in results:
            if card.name == cardname and card.image_url is not None:
                deck.add_card(card)
                break
            continue

            """



class Deck(collections.Iterable):

    # Colors of the cards don't change, so we make this a class variable
    color_ids = 'B', 'U', 'G', 'R', 'W', None

    def __init__(self, cards = [] ):
        self.cards = [get_card_by_name(card) for card in cards] if cards and type(cards[0]) is str else cards

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
        max = max()
        return []

    @property
    def manaColorProportions(self):
        for card in self.cards:
            print(card.mana_cost)

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

    def get_card(self, cardNameStr):
        return next(card for card in self.cards if card.name == cardNameStr)

    def add_card(self, card):
        """Should be called with a string or a Card object"""
        #self.cards.append(card) if type(card) == Card else self.cards.append(get_card_by_name(card))
        self.cards.append(card) if type(card) is Card else self.cards.append(get_card_by_name(card))



a = Deck(["LLanowar Elves", "Swords to plowshares"])

print(a)