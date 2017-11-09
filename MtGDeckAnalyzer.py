import tkinter
from tkinter import filedialog
import MtGUtils as mgu
from Deck import Deck
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


default_decklist = """Llanowar elves
Brainstorm
Swords to plowshares
Lightning Storm
Drain Life
Myr Galvanizer
"""


# May want to later add functionality here, so abstracted it out
class Client:
    """The client class exposes functionality to create an instance of our application.
       It is created for pre-processing such as loading a default deck."""

    def __init__(self):
        self.root = tkinter.Tk()
        defDeck = Deck(default_decklist.splitlines())
        self.ui = MainPage(self.root, deck=defDeck)
        self.ui.pack()

    def display(self):
            self.root.mainloop()


class MainPage(tkinter.Frame):
    """MainPage is where we compose all the tkinter UI elements and associated resources into one working application.
       Packing of the widgets is all done at the bottom."""

    # Callback for FileMenu commands
    def open_deck(self):
        filename = filedialog.askopenfilename(initialdir="/home/Eredea/PycharmProjects/MagicTheGathering",
                                              title="Select file",
                                              filetypes=( ("all files", "*.*"),("jpeg files", "*.jpg")))
        with open(filename) as f:
            self.deckListDisplay.show_deck(Deck([x.strip() for x in f]))

    def save_deck(self, deck):
        file = filedialog.asksaveasfilename()
        with open(file, "w+") as f:
            f.write(str(deck))

    def __init__(self, master, deck=Deck()):
        super().__init__(master)
        self.deck = deck

        menubar = tkinter.Menu(self)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command = self.open_deck)
        filemenu.add_command(label="Save", command = lambda: self.save_deck(self.deck))
        filemenu.add_separator()
        menubar.add_cascade(label="File", menu=filemenu)
        master.config(menu=menubar)


        self.leftDisplay = LeftDisplay(self,bg= 'black',width = 50,borderwidth = 1,relief = 'raised')
        self.leftDisplay.deckListButton['command'] = lambda: self.add_to_deck_list(self.leftDisplay.displayedCard)
        self.leftDisplay.cardPoolButton['command'] = lambda: self.add_to_card_pool(self.leftDisplay.displayedCard)

        # This is the card pool display spanning the bottom of the screen.
        self.cardPoolDisplay = DeckListDisplay(self, linkedDisplay=True, width =100, height =20)

        self.stats_viewer = StatisticViewer(self)
        self.stats_viewer.updateButton['command'] = lambda: self.stats_viewer.reAnalyze(self.deck)
        self.stats_viewer.reAnalyze(self.deck)

        self.deckListDisplay = DeckListDisplay(self, linkedDisplay=True, height = 40, width = 30)
        self.deckListDisplay.show_deck(deck)

        self.leftDisplay.pack(fill='y', side='left')
        self.cardPoolDisplay.pack(fill='both', side='bottom')
        self.deckListDisplay.pack(fill = 'both', side = 'right')
        self.stats_viewer.pack()
        tkinter.Label(text = "Your card pool:").pack()


    def display_card(self, card):
        # For now just uses left's display, but we could add functionality later
        self.leftDisplay.display_card(card)

    def add_to_card_pool(self,card):
        self.cardPoolDisplay.add_card(card)

    def add_to_deck_list(self, card):
            self.deckListDisplay.add_card(card)
            self.deck.add_card(card)


# Here are individual frame objects that make up the MainPage frame:
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
        self.displayedCard = mgu.get_card_by_name("Swords to Plowshares")

        # Placeholder image object
        self.image = mgu.get_card_picture(self.displayedCard)

        # The display of the current card is created and placed.
        self.cardImageBox = tkinter.Label(self, bg='black',image=self.image, height=300, width=300)
        self.cardImageBox.image = self.image

        # Here we create the text that displays MtG information about the card
        self.cardInfoDisplay = tkinter.Message(self, text="Card Information will be displayed here.", justify='left')

        # Search box for cards and corresponding results, by name
        self.cardSearchBox = tkinter.Entry(self)
        self.cardSearchBox.insert(0, "Swords to plowshares")
        self.searchResultsList = DeckListDisplay(self, linkedDisplay=True)

        # Buttons
        self.searchButton = tkinter.Button(self, text="Search for card", command= lambda: self.searchResultsList.show_deck(mgu.search(name = self.cardSearchBox.get())))
        self.deckListButton = tkinter.Button(self, font = 'Times', bg='black', fg= 'white', text="Add to DeckList")
        self.cardPoolButton = tkinter.Button(self, font = 'Times', bg='black', fg= 'white', text="Add to Cardpool")
        self.advancedSearchButton = tkinter.Button(self, text = "Bring advanced search", command = lambda: AdvancedSearchWindow(self.master))

        # Pack is the geometry manager for tkinter UI widgets- places them on the screen
        self.cardImageBox.pack(side='top')
        self.cardInfoDisplay.pack(fill='both')
        self.searchResultsList.pack(fill='both')
        self.cardSearchBox.pack()
        self.searchButton.pack()
        self.deckListButton.pack()
        self.cardPoolButton.pack()
        self.advancedSearchButton.pack()

    def display_card(self, card):

        if type(card) is str:
            print("Used str, should almost never happen")
            card = mgu.get_card_by_name(card)
        image = mgu.get_card_picture(card)
        self.cardImageBox.config(image = image)
        # This is necessary because tkinter doesn't update python, so we need to hold on to the reference
        self.cardImageBox.image = image

        self.cardInfoDisplay.config(text = card.set_name + " " + card.text if card.text else card.set_name)
        self.displayedCard = card


class StatisticViewer(tkinter.Frame):

    pieChartColors = ['black', 'blue', 'green', 'red', 'white', 'yellow']
    pieChartLabels = ['Black', 'Blue', 'Green', 'Red', 'White', 'Colorless']


    def __init__(self, master, **kwargs):
        super().__init__(master, kwargs)

        #We have two figures used to display graphics
        f1 = Figure(figsize=(5, 5), dpi=100)
        f2 = Figure(figsize=(5, 5), dpi=100)
        sizes = [16,16,16,16,16, 16]

        self.f1SubPlot = f1.add_subplot(111)
        self.f1SubPlot.pie(sizes, labels = StatisticViewer.pieChartLabels, colors = StatisticViewer.pieChartColors, explode=[0,0,0,.1,0,0], shadow=True, autopct='%1.1f%%')
        self.canvas1 = FigureCanvasTkAgg(f1, self)
        self.canvas1.show()
        self.canvas1.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH)



        self.f2SubPlot = f2.add_subplot(111)
        self.f2SubPlot.hist([1,2,3,4,5,6,7,8,9])
        self.canvas2 = FigureCanvasTkAgg(f2, self)
        self.canvas2.show()
        self.canvas2.get_tk_widget().pack(side=tkinter.RIGHT, fill=tkinter.BOTH)

        self.updateButton = tkinter.Button(self)
        self.updateButton.pack(side = tkinter.BOTTOM)


    def reAnalyze(self, deck):
        self.f1SubPlot.clear()
        self.f1SubPlot.pie(deck.manaColorProportions, labels = StatisticViewer.pieChartLabels, colors = StatisticViewer.pieChartColors, explode=[0,0,0,.1,0,0], shadow=True, autopct='%1.1f%%')
        self.canvas1.draw()

        self.f2SubPlot.clear()
        self.f2SubPlot.hist([card.cmc for card in deck])
        self.canvas2.draw()
        pass


# This is a custom window to open for advanced search functionality
class AdvancedSearchWindow(tkinter.Toplevel):
    # Use list here because it is ordered and this populates option box
    searchableFilters = [ 'name', 'type', 'cmc', 'rarity', 'setName', 'text', 'power', 'set', 'id', 'originalType', 'flavor',
                         'watermark', 'printings', 'subtypes', 'originalText', 'toughness', 'types', 'number',
                         'artist', 'layout',  'imageUrl', 'legalities', 'foreignNames', 'manaCost',
                          'multiverseid']

    def __init__(self, parent):
        super().__init__(parent)

        self.horizontal = tkinter.Frame(self)

        choices = ['AND','OR','NOT']
        self.variable = tkinter.StringVar(self)
        self.variable.set("AND")
        self.andOrBox = tkinter.OptionMenu(self.horizontal, self.variable, *choices)

        self.filterName = tkinter.StringVar(self)
        self.filterName.set("name")
        self.filterBox = tkinter.OptionMenu(self.horizontal, self.filterName, *AdvancedSearchWindow.searchableFilters)

        self.searchBox = tkinter.Entry(self.horizontal)
        self.andOrBox.pack(side = 'left')
        self.filterBox.pack(side = 'left')
        self.searchBox.pack(side = 'left')

        self.resultBox = DeckListDisplay(self, linkedDisplay=True)
        self.filterDict ={}

        def searchButton():
            # I like this solution better than lambdas
            self.resultBox.show_deck(mgu.search(**self.filterDict))

        self.searchButton = tkinter.Button(self, command = searchButton, text="Search for your card")

        def add_filter():
            self.filterDict[self.filterName.get()] = self.searchBox.get()
            self.activeFilters.insert('end', self.filterName.get() + ' ' + self.searchBox.get())

        self.horizontal2 = tkinter.Frame(self)
        self.addFilterButton = tkinter.Button(self.horizontal2, command = add_filter, text = "Add a filter" )
        self.removeFilterButton = tkinter.Button(self.horizontal2)
        self.addFilterButton.pack(side = 'left')
        self.removeFilterButton.pack(side = 'left')


        self.activeFilters = tkinter.Listbox(self)
        self.image = mgu.get_card_picture(mgu.get_card_by_name("Swords to plowshares"))
        self.cardImageBox = tkinter.Label(self, image = self.image, height=300, width=300)

        self.activeFilters.pack()
        self.horizontal2.pack()
        self.horizontal.pack()
        self.resultBox.pack()
        self.searchButton.pack()
        self.cardImageBox.pack()



    def display_card(self, card):
        image = mgu.get_card_picture(card)
        self.cardImageBox.config(image = image)
        # This is necessary because tkinter doesn't update python, so we need to hold on to the reference
        self.cardImageBox.image = image
        # We could later just implement a card.displayInfo property, but extending card is hard because of how they're built. Will have to change module


# Custom Tk widget used in various frames
class DeckListDisplay(tkinter.Listbox):
    """Custom tkinter Listbox widget which automatically binds the click-list event."""

    def __init__(self, masterFrame, linkedDisplay = False, deck = Deck(), **kwargs):
        self.masterFrame = masterFrame
        super().__init__(self.masterFrame, kwargs)

        self.deck = deck

        self.linkedDisplay = linkedDisplay
        if self.linkedDisplay:
            self.bind('<<ListboxSelect>>', self.click_deck_list)

        self.bind('<Double-1>', self.doubleclick)

    def add_card(self, card):
        card = card if type(card) is mgu.Card else mgu.get_card_by_name(card)
        self.insert('end',card.name)
        self.deck.add_card(card)

    def doubleclick(self, event):
        w = event.widget
        if w.curselection():
            index = int(w.curselection()[0])
            card = self.deck[index]
            image = mgu.get_card_picture(card)
        window = tkinter.Toplevel(self.masterFrame)
        window.attributes("-topmost", True)
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
            card = self.deck[w.get(index)]
            self.masterFrame.display_card(card)

    @property
    def selectedCard(self):
        pass

if __name__ == "__main__":
    Client().display()