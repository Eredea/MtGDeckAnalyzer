
import tkinter
from Model import *
import wget
from PIL import Image, ImageTk
import os


class MyUi:

    def __init__(self):
        """The program starts by creating a new instance of the MyUi class."""
        top = tkinter.Tk()

        self.displayedCard = get_card_by_name("Khalni Hydra")

        #This frame is used to organize the search bar and search results sections.
        self.leftDisplay = tkinter.Frame(top, width = 50, borderwidth = 1, relief = 'raised')
        self.leftDisplay.pack(fill = 'y',side ='left')

        image = Image.open("Khalni Hydra.png")
        photo = ImageTk.PhotoImage(image)
        self.cardImageBox = tkinter.Label(self.leftDisplay, image = photo )
        self.cardImageBox.pack(side = 'top')

        self.cardInfoDisplay = tkinter.Label(self.leftDisplay, text= "Card Information will be displayed here.")
        self.cardInfoDisplay.pack(fill = 'y')

        self.searchResultsList = tkinter.Listbox(self.leftDisplay)
        self.searchResultsList.bind('<<ListboxSelect>>', self.click_deck_list)
        self.searchResultsList.pack(fill = 'both')

        self.cardSearchBox = tkinter.Entry(self.leftDisplay)
        self.cardSearchBox.insert(0, "Search for a card")
        self.cardSearchBox.pack()

        #Used lambda here because the command needs to be callable, but I wanted to send parameters.
        self.searchButton = tkinter.Button(self.leftDisplay, command= lambda: self.search_card(self.cardSearchBox.get()), text= "Search for Card")
        self.searchButton.pack()

        self.deckListButton = tkinter.Button(self.leftDisplay, command= self.add_to_deck_list, text="Add to DeckList")
        self.deckListButton.pack()

        self.deckListDisplay = tkinter.Listbox(top, width=100, height = 20)
        self.deckListDisplay.anchor('s')
        self.deckListDisplay.bind('<<ListboxSelect>>', self.click_deck_list)
        self.deckListDisplay.pack(fill ='both', side= 'bottom')



        top.mainloop()

    def display_card(self, cardName):
        #Am wondering about this, don't know whether to put the download card logic in the model or view.
        card = get_card_by_name(cardName)

        imageLoc = "{}.png".format(cardName)
        if not os.path.isfile(imageLoc):
            wget.download(card.image_url, out=imageLoc)
        cardImage = ImageTk.PhotoImage(Image.open(imageLoc))

        self.cardImageBox.config(image = cardImage)
        # Delete this and show what happens to ask about garbage collection.
        self.cardImageBox.image = cardImage

        self.cardInfoDisplay.config(text = card.set_name + " " + card.text)
        self.displayedCard = card


    # Callback for searchButton
    def search_card(self, cardName):
        # When Searching I could populate all results and have them stored ready to clickm
        # Right now I just display the search results and then when clicking the listbox create another card item
        cards = Card.where(name=cardName).all()
        cardNames = set([card.name for card in cards])
        for name in cardNames:
            self.searchResultsList.insert('end', name)

    #Callback for deckListButton
    def add_to_deck_list(self):
        self.deckListDisplay.insert('end', self.displayedCard.name)

    def click_deck_list(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.display_card(value)

    cardInfo = """
    Name: {}
    Set: {}
    Rarity: {}
    Card Text: {}
    """


start = MyUi()