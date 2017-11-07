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
Brainstorm
Swords to plowshares
Lightning Storm
Drain Life
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

class MainPage:


    def __init__(self, master, deck=Deck()):
        """MainPage is where we compose all the tkinter UI elements and associated resources into one working application.
           Packing of the widgets is all done at the bottom."""
        self.deck = deck
        self.master = master
        self.master.display_card = self.display_card


        self.leftDisplay = LeftDisplay(self.master,bg= 'black',width = 50,borderwidth = 1,relief = 'raised')
        self.leftDisplay.deckListButton['command'] = lambda: self.add_to_deck_list(self.leftDisplay.displayedCard)
        self.leftDisplay.cardPoolButton['command'] = lambda: self.add_to_card_pool(self.leftDisplay.displayedCard)

        # This is the card pool display spanning the bottom of the screen.
        self.cardPoolDisplay = CardListDisplay(self.master, linkedDisplay=True, width =100, height =20)

        self.stats_viewer = StatisticViewer(self.master)
        self.statsButton = tkinter.Button(self.master, command= lambda: self.stats_viewer.refreshFigure(self.deck.manaColorProportions))

        self.deckListDisplay = CardListDisplay(self.master, linkedDisplay=True, height = 40, width = 30)
        self.deckListDisplay.show_deck(deck)

        self.leftDisplay.pack(fill='y', side='left')
        self.cardPoolDisplay.pack(fill='both', side='bottom')
        self.deckListDisplay.pack(fill = 'both', side = 'right')
        self.stats_viewer.pack()
        self.statsButton.pack()
        tkinter.Label(text = "Your card pool:").pack()

    def start_UI(self):
        self.master.mainloop()

    def display_card(self, card):
        # For now just uses left's display, but we could add functionality later
        self.leftDisplay.display_card(card)

    def add_to_card_pool(self,card):
        self.cardPoolDisplay.add_card(card)

    def add_to_deck_list(self, card):
            self.deckListDisplay.add_card(card)
            self.deck.add_card(card)

#Here are individual frame objects that make up the mainpage "master" frame:
class LeftDisplay(tkinter.Frame):
    cardInfo = """
    Name: {}
    Set: {}
    Rarity: {}
    Card Text: {}
    """

    def __init__(self, parent, **kwargs):
        """Creates and configures widgets that will be placed on the left side of the screen.
            Packing is done at the end."""
        super().__init__(parent, kwargs)
        self.parent = parent

        # There is always one displayed card in this area, and functions act around it.
        self.displayedCard = get_card_by_name("Khalni Hydra")

        # Placeholder image object
        self.image = get_card_picture(self.displayedCard)

        # The display of the current card is created and placed.
        self.cardImageBox = tkinter.Label(self, bg='black',image=self.image, height=300, width=300)
        self.cardImageBox.image = self.image

        #Here we create the text that displays MtG information about the card

        self.cardInfoDisplay = tkinter.Message(self, text="Card Information will be displayed here.", justify='left')

        #Searchbox for cards and corresponding results
        self.cardSearchBox = tkinter.Entry(self)
        self.cardSearchBox.insert(0, "Swords to plowshares")
        self.searchResultsList = CardListDisplay(self, linkedDisplay=True)

        self.searchButton = tkinter.Button(self, command=lambda: self.search_card(self.cardSearchBox.get()),text="Search for Card")

        # Here is a design point maybe
        # When the button is clicked, we need to both alter the display and update the APPLICATION's current deck values
        # We could from the MYUI class do self.leftdisplay.deckListButton[command] from a place where we have more scope
        # But now our code is more seperated.
        self.deckListButton = tkinter.Button(self, font = 'Times', bg='black', fg= 'white', text="Add to DeckList")
        self.cardPoolButton = tkinter.Button(self, font = 'Times', bg='black', fg= 'white', text="Add to Cardpool")
        self.advancedSearchButton = tkinter.Button(self, text = "Bring advanced search", command = self.advanced_search)


        self.cardImageBox.pack(side='top')
        self.cardInfoDisplay.pack(fill='both')
        self.searchResultsList.pack(fill='both')
        self.cardSearchBox.pack()
        self.searchButton.pack()
        self.deckListButton.pack()
        self.cardPoolButton.pack()
        self.advancedSearchButton.pack()

    def advanced_search(self):
        window = tkinter.Toplevel(self.parent)

        horizontal = tkinter.Frame(window)

        frameObj = tkinter.Frame(window, height = 300, width = 300)

        choices = ['AND','OR','NOT']
        variable = tkinter.StringVar(window)
        variable.set("AND")
        andOrBox = tkinter.OptionMenu(horizontal, variable, *choices)
        andOrBox.pack(side = 'left', )


        searchBox = tkinter.Entry(horizontal)
        searchBox.pack(side = 'left')

        resultBox = CardListDisplay(window)

        searchButton = tkinter.Button(window, command = lambda: adv_search_card(searchBox.get()))

        searchButton.pack()
        horizontal.pack()
        resultBox.pack()
        frameObj.pack()


        def adv_search_card(cardName):
            results = Deck.search(cardName)
            resultBox.show_deck(results)

    def display_card(self, card):

        if type(card) is str:
            print("Used str, should almost never happen")
            card = get_card_by_name(card)
        print("card for display_card", card)
        image = get_card_picture(card)
        self.cardImageBox.config(image = image)
        # This is necessary because tkinter doesn't update python, so we need to hold on to the reference
        self.cardImageBox.image = image
        # We could later just implement a card.displayInfo property, but extending card is hard because of how they're built. Will have to change module
        self.cardInfoDisplay.config(text = card.set_name + " " + card.text if card.text else card.set_name)
        self.displayedCard = card

    # Callback for searchButton
    def search_card(self, cardName):
        # When Searching I could populate all results and have them stored ready to click
        # Right now I just display the search results and then when clicking the listbox create another card item
        searchResults = search(cardName)
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

# Here are custom tk widgets used in the MainPage class
class CardListDisplay(tkinter.Listbox):
    """Custom tkinter Listbox widget which automatically binds the click-list event."""
    def __init__(self, masterFrame, linkedDisplay = False, deck = Deck(), **kwargs, ):
        self.masterFrame = masterFrame
        super().__init__(self.masterFrame, kwargs)

        self.deck = deck
        self.linkedDisplay = linkedDisplay
        if self.linkedDisplay:
            self.bind('<<ListboxSelect>>', self.click_deck_list)
        self.bind('<Double-1>', self.doubleclick)
    def add_card(self, card):
        card = card if type(card) is Card else get_card_by_name(card)
        self.insert('end',card.name)
        self.deck.add_card(card)

    def doubleclick(self, event):
        w = event.widget
        if w.curselection():
            index = int(w.curselection()[0])
            card = self.deck.get_card(w.get(index))
            image = get_card_picture(card)
        window = tkinter.Toplevel(self.masterFrame)
        picture = tkinter.Label(window, image = image)
        picture.pack()
        picture.image = image

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