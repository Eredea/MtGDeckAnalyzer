from mtgsdk import Card
from mtgsdk import Set
from mtgsdk import Type
from mtgsdk import Supertype
from mtgsdk import Subtype
from mtgsdk import Changelog

import tkinter
import wget
from PIL import Image, ImageTk


def search_card_by_name(name):
    """ This takes in a card name, and returns a single card object.
        When using the API, a search for a single card by name returns an object of the card for every set it was printed in.
        This is to get around that.
        :param name: Name of the card to search
        :returns: Card object
        """
    card = Card.where(name = name).all()[0]
    return card

def get_card_picture(name):
    """:param name: string of card's name
       :returns ImageTk.PhotoImage of
    """
    cards = Card.where(name = name).all()
    for card in cards:
        if isinstance(card.image_url, str) and card.image_url is not "None":
            imageLoc = "{}.png".format(name)
            wget.download(card.image_url, out=imageLoc)
            image = Image.open(imageLoc)
            photo = ImageTk.PhotoImage(image)
            return photo

top = tkinter.Tk()

image = Image.open("Default.png")
photo = ImageTk.PhotoImage(image)
cardImageBox = tkinter.Label(top, image = photo )
cardImageBox.pack()


cardSearchBox = tkinter.Entry(top)
cardSearchBox.insert(0, "Type your text here")
cardSearchBox.pack()




#defaultImage = tkinter.PhotoImage(file = "Default.jpg")

#Callback for searchButton
def display_picture():
    pictureObj = get_card_picture(cardSearchBox.get())
    cardImageBox.config(image = pictureObj)
    cardImageBox.image = pictureObj


searchButton = tkinter.Button(top, text = "Display Card", command = display_picture)
searchButton.pack()

def add_to_deck_list()=



top.mainloop()
