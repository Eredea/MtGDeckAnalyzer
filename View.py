import tkinter
from Model import *
from PIL import Image, ImageTk
from urllib.request import urlopen
from io import BytesIO

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


default_decklist = """Llanowar elves
Dark Ritual
Swords to plowshares
"""


class Client:
    """The client class exposes functionality to create an instance of our application."""
# May want to later add functionality here, so abstracted it out

    def __init__(self):
        self.root = tkinter.Tk()
        def_deck = Deck(default_decklist.splitlines())
        self.ui = MainPage(self.root, deck=def_deck)

    def new_instance(self):
        self.ui.start_UI()

    #Not even used in the app yet
    cardInfo = """
    Name: {}
    Set: {}
    Rarity: {}
    Card Text: {}
    """


# Here are custom tk widgets used in the MainPage class
class CardListDisplay(tkinter.Listbox):
    def __init__(self, masterFrame, linkedLabel = None, **kwargs, ):
        self.masterFrame = masterFrame
        #Under this super call I'm wondering the differences if I refer to self.masterFrame or not
        super().__init__(self.masterFrame, kwargs)
        self.bind('<<ListboxSelect>>', self.click_deck_list)


    def click_deck_list(self, evt):
        w = evt.widget
        print("Hi1")
        if w.curselection():
            print("Hi2")
            index = int(w.curselection()[0])
            cardName = w.get(index)
            self.masterFrame.display_card(cardName)


class MainPage:


    def __init__(self, master, deck=Deck()):
        self.deck = deck

        # Here is a solution to a problem of "How do we update a widget on a different frame"
        # They all have a reference to master, so we can call things from master and assign them here.
        self.master = master
        self.master.display_card = self.display_card

        # This frame is used to organize the search bar and search results sections on the left.
        self.leftDisplay = LeftDisplay(self.master, width = 50, borderwidth = 1, relief = 'raised')

        """
        # Here is similar logic to the first commit in the initname
        self.leftDisplay.deckListButton['command'] = lambda: self.add_to_deck_list(self.leftDisplay.displayedCard.name)
        self.leftDisplay.pack(fill = 'y', side = 'left')"""

        # Here is similar logic to the first commit in the init
        self.leftDisplay.deckListButton['command'] = lambda: self.add_to_deck_list(self.leftDisplay.displayedCard.name)
        self.leftDisplay.pack(fill='y', side='left')

        #self.deckListDisplay = tkinter.Listbox(self.master, width=100, height=20)
        #self.deckListDisplay.bind('<<ListboxSelect>>', self.click_deck_list)
        #self.deckListDisplay.pack(fill='both', side='bottom')

        # This is the card pool display spanning the bottom of the screen.
        self.deckListDisplay = CardListDisplay(self.master, width =100, height =20 )
        if self.deck.cards:
            for card in self.deck.cards:
                self.deckListDisplay.insert('end',card.name)

        self.deckListDisplay.pack(fill='both',side='bottom')

        self.stats_viewer = StatisticViewer(self.master)
        self.stats_viewer.pack()

        self.updateButton = tkinter.Button(self.master, command= lambda: self.stats_viewer.refreshFigure(self.deck.mana_curve_proportions))
        self.updateButton.pack()



    def display_card(self, cardName ):
        self.leftDisplay.display_card(cardName)

    def click_deck_list(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)


    def add_to_deck_list(self, cardName):
            self.deckListDisplay.insert('end', cardName)
            self.deck.cards.append(get_card_by_name(cardName))


    def start_UI(self):
        self.master.mainloop()


#Here are individual frame objects that make up the main frame:
class LeftDisplay(tkinter.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, kwargs)

        # There is always one displayed card in this area, and functions act around it.
        self.displayedCard = get_card_by_name("Khalni Hydra")

        # Placeholder image object
        self.image = Image.open("Khalni Hydra.png")
        self.photo = ImageTk.PhotoImage(self.image)

        # The display of the current card is created and placed.
        self.cardImageBox = tkinter.Label(self, image=self.photo, height=300, width=300)
        self.cardImageBox.image = self.photo
        self.cardImageBox.pack(side='top')

        #Here we create the text that displays MtG information about the card
        self.cardInfoDisplay = tkinter.Label(self, text="Card Information will be displayed here.")
        self.cardInfoDisplay.pack(fill='y')

        #Searchbox for cards and corresponding results
        self.cardSearchBox = tkinter.Entry(self)
        self.cardSearchBox.insert(0, "Search for a card")
        self.searchResultsList = CardListDisplay(self)

        #Order of packing matters, we want results on top
        self.searchResultsList.pack(fill='both')
        self.cardSearchBox.pack()

        #The button to search
        # Used lambda here because the command needs to be callable, but I wanted to send parameters.
        # CRITIQUE: Here, I think I should take the search_card command away from self
        # Within the MYUi object, we could declare the command.
        self.searchButton = tkinter.Button(self, command=lambda: self.search_card(self.cardSearchBox.get()),
                                           text="Search for Card")
        self.searchButton.pack()

        # Here is a design point
        # When the button is clicked, we need to both alter the display and update the APPLICATION's current deck values
        # We could from the MYUI class do self.leftdisplay.deckListButton[command] from a place where we have more scope
        self.deckListButton = tkinter.Button(self, text="Add to DeckList")
        self.deckListButton.pack()

    def display_card(self, card):

        if type(card) is not Card:
            card = get_card_by_name(card)

        # We ultimately create an Image object after downloading from a url, reading the raw data with a context manager
        # and recreating it from its bytes
        a =Image.open(BytesIO(urlopen(card.image_url).read()))
        cardImage = ImageTk.PhotoImage(a)

        # This updates the image shown
        self.cardImageBox.config(image = cardImage)
        # This is necessary because tkinter doesn't update python, so we need to hold on to the reference
        self.cardImageBox.image = cardImage

        # This updates the text
        self.cardInfoDisplay.config(text = card.set_name + " " + card.text)

        # We update this so other functions in the class can work with the card
        # I know some of these comments are totally unnecessary to read
        self.displayedCard = card

    # Callback for searchButton
    def search_card(self, cardName):
        # When Searching I could populate all results and have them stored ready to click
        # Right now I just display the search results and then when clicking the listbox create another card item
        cards = Card.where(name=cardName).all()
        cardNames = set([card.name for card in cards])
        self.searchResultsList.delete(0, 'end')
        for name in cardNames:
            self.searchResultsList.insert('end', name)


class StatisticViewer(tkinter.Frame):

    pieChartColors = ['black', 'blue', 'green', 'red', 'white', 'yellow']
    pieChartLabels = ['Black', 'Blue', 'Green', 'Red', 'White', 'Colorless']


    def __init__(self, master, **kwargs):
        super().__init__(master, kwargs)

        f = Figure(figsize=(5, 5), dpi=100)
        self.a = f.add_subplot(111)
        #a.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])

        labels = 'Red', 'Green', 'Black', 'White', 'Blue'
        sizes = [20,20,20,20,20, 0]
        self.a.pie(sizes, labels = StatisticViewer.pieChartLabels, colors = StatisticViewer.pieChartColors, explode=[0,0,0,.1,0,0], shadow=True, autopct='%1.1f%%')

        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    def refreshFigure(self, sizes):
        self.a.clear()
        self.a.pie(sizes, labels = StatisticViewer.pieChartLabels, colors = StatisticViewer.pieChartColors, explode=[0,0,0,.1,0,0], shadow=True, autopct='%1.1f%%')
        self.canvas.draw()

    def reAnalyze(self, deck):
        pass

if __name__ == "__main__":
    start = Client().new_instance()