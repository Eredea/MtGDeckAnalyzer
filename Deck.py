import collections
import MtGUtils


class Deck(collections.MutableSequence):
    # Colors of the cards don't change, so we make this a class variable
    color_ids = 'B', 'U', 'G', 'R', 'W', None

    def __init__(self, cards = [] ):
        """A deck can be initialized with no parameters, with a list of strings, or a list of card objects."""
        self.cards = [MtGUtils.get_card_by_name(card) for card in cards] if cards and type(cards[0]) is str else cards

    def __iter__(self):
        for card in self.cards:
            yield card

    def __len__(self):
        return len(self)

    def __str__(self):
        return '\n'.join([card.name for card in self])

    def __delitem__(self, index):
        del(self.cards[index])

    def __setitem__(self, key, value):
        self.cards[key] = value if type(value) is MtGUtils.Card else MtGUtils.get_card_by_name(value)

    def insert(self, index, value):
        self.cards.insert(index,value)

    def __getitem__(self, search):
        return next(card for card in self.cards if card.name == search) if type(search) is str else self.cards[search]

    def add_card(self, card):
        """Should be called with a string or a Card object"""
        #self.cards.append(card) if type(card) == Card else self.cards.append(get_card_by_name(card))
        self.cards.append(card) if type(card) is MtGUtils.Card else self.cards.append(MtGUtils.get_card_by_name(card))


    @property
    def mean_mana(self):
        return sum([card.cmc for card in self])/len(self)


    @property
    def mana_curve_tuple(self):
        maxr = range(max(card.cmc for card in self))
        return []

    @property
    def manaColorProportions(self):
        # I'm sure this area could be chopped down
        colors = [card.color_identity[0] if isinstance(card.color_identity, list) else None for card in self.cards]
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
