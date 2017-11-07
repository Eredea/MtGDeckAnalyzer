import tkinter
from MtGUtils import *
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

# May want to later add functionality here, so abstracted it out
class Client:
    """The client class exposes functionality to create an instance of our application.
       It is created for pre-processing such as loading a default deck."""

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
    """Custom tkinter Listbox widget which automatically binds the click-list event."""
    def __init__(self, masterFrame, linkedDisplay = False, deck = Deck(), **kwargs, ):
        # Under this super call I'm wondering the differences if I refer to self.masterFrame or not
        # I don't think there's a difference here.
        self.masterFrame = masterFrame
        super().__init__(self.masterFrame, kwargs)

        self.deck = deck
        self.linkedDisplay = linkedDisplay
        if self.linkedDisplay:
            self.bind('<<ListboxSelect>>', self.click_deck_list)

    def add_card(self, card):
        card = card if type(card) is Card else get_card_by_name(card)
        self.insert('end',card.name)
        self.deck.add_card(card)


    def show_deck(self, deck):
        """Updates listbox UI with card names from deck object."""
        self.deck = deck
        self.delete(0,'end')
        for card in deck:
            self.insert('end', card.name)


    def click_deck_list(self, evt):
        w = evt.widget
        if w.curselection():
            index = int(w.curselection()[0])
            cardName = w.get(index)
            card = self.deck.get_card(cardName)
            print(card)
            print(card.name)
            self.masterFrame.display_card(card)

    @property
    def selectedCard(self):
        pass


class MainPage:


    def __init__(self, master, deck=Deck()):
        """MainPage is where we compose all the tkinter UI elements and associated resources into one working application.
           Packing of the widgets is all done at the bottom."""
        self.deck = deck
        self.master = master
        self.master.display_card = self.display_card


        self.leftDisplay = LeftDisplay(self.master,
                                       bg= 'black',
                                       width = 50,
                                       borderwidth = 1,
                                       relief = 'raised')
        self.leftDisplay.deckListButton['command'] = lambda: self.add_to_deck_list(self.leftDisplay.displayedCard)

        # This is the card pool display spanning the bottom of the screen.
        self.deckListDisplay = CardListDisplay(self.master, linkedDisplay=True, width =100, height =20 )
        self.deckListDisplay.show_deck(deck)

        self.stats_viewer = StatisticViewer(self.master)
        self.statsButton = tkinter.Button(self.master, command= lambda: self.stats_viewer.refreshFigure(self.deck.manaColorProportions))


        self.leftDisplay.pack(fill='y', side='left')
        self.deckListDisplay.pack(fill='both',side='bottom')
        self.stats_viewer.pack()
        self.statsButton.pack()

    def start_UI(self):
        self.master.mainloop()

    def display_card(self, card):
        self.leftDisplay.display_card(card)


    def add_to_deck_list(self, card):
            self.deckListDisplay.add_card(card)
            self.deck.add_card(card)

#Here are individual frame objects that make up the main frame:
class LeftDisplay(tkinter.Frame):

    def __init__(self, parent, **kwargs):
        """Creates and configures widgets that will be placed on the left side of the screen.
            Packing is done at the end."""
        super().__init__(parent, kwargs)

        # There is always one displayed card in this area, and functions act around it.
        self.displayedCard = get_card_by_name("Khalni Hydra")

        # Placeholder image object
        self.image = Image.open("Khalni Hydra.png")
        self.photo = ImageTk.PhotoImage(self.image)

        # The display of the current card is created and placed.
        self.cardImageBox = tkinter.Label(self, bg='black',image=self.photo, height=300, width=300)
        self.cardImageBox.image = self.photo

        #Here we create the text that displays MtG information about the card
        self.cardInfoDisplay = tkinter.Label(self, text="Card Information will be displayed here.", height = 5, width = 50, )

        #Searchbox for cards and corresponding results
        self.cardSearchBox = tkinter.Entry(self)
        self.cardSearchBox.insert(0, "Swords to plowshares")
        self.searchResultsList = CardListDisplay(self, linkedDisplay=True)

        self.searchButton = tkinter.Button(self, command=lambda: self.search_card(self.cardSearchBox.get()),text="Search for Card")

        # Here is a design point
        # When the button is clicked, we need to both alter the display and update the APPLICATION's current deck values
        # We could from the MYUI class do self.leftdisplay.deckListButton[command] from a place where we have more scope
        self.deckListButton = tkinter.Button(self, font = 'Times', bg='black', fg= 'white', text="Add to DeckList")

        self.cardImageBox.pack(side='top')
        self.cardInfoDisplay.pack(fill='y')
        self.searchResultsList.pack(fill='both')
        self.cardSearchBox.pack()
        self.searchButton.pack()
        self.deckListButton.pack()

    def display_card(self, card):

        if type(card) is str:
            print("Used str")
            card = get_card_by_name(card)
        print("card for display_card", card)
        image = get_card_picture(card)
        self.cardImageBox.config(image = image)
        # This is necessary because tkinter doesn't update python, so we need to hold on to the reference
        self.cardImageBox.image = image
        self.cardInfoDisplay.config(text = card.set_name + " " + card.text)
        self.displayedCard = card

    # Callback for searchButton
    def search_card(self, cardName):
        # When Searching I could populate all results and have them stored ready to click
        # Right now I just display the search results and then when clicking the listbox create another card item
        searchResults = Deck.search(cardName)
        self.searchResultsList.show_deck(searchResults)

class StatisticViewer(tkinter.Frame):

    pieChartColors = ['black', 'blue', 'green', 'red', 'white', 'yellow']
    pieChartLabels = ['Black', 'Blue', 'Green', 'Red', 'White', 'Colorless']


    def __init__(self, master, **kwargs):
        super().__init__(master, kwargs)

        f = Figure(figsize=(5, 5), dpi=100)
        self.a = f.add_subplot(111)


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


def get_card_picture(card):
    """:param card: Card object
       :returns ImageTk.PhotoImage of Card
    """
    # We ultimately create an Image object after downloading from a url, reading the raw data with a context manager
    # and recreating it from its bytes
    imageFileObject = Image.open(BytesIO(urlopen(card.image_url).read()))
    cardImage = ImageTk.PhotoImage(imageFileObject)
    return cardImage

if __name__ == "__main__":
    start = Client().new_instance()