import random

class Card():
   """
   A class for representing a single playing card (no jokers).
   """
   
   # constructor
   def __init__(self, f, s):
   # unnecessary declarations, but here for readability
      self.suit = "?"
      self.face = "?"
      self.value = 0
   
      # set the suit
      if s == "H" or s == "S" or s == "D" or s == "C":
         self.suit = s
      else:
         raise Exception("Invalid suit value in bjcard.py")
      
       # set the face; checked for vaild input when the value is set
      self.face = f
      # set the value. value = face, if face is a number
      try:
         self.value = int(self.face)
      # if the face isn't a number, assign the value
      except: 
         if self.face == "A":
            self.value = 1 # 11 option handled in bjhand.py
         elif self.face == "J" or self.face == "Q" or self.face == "K":
            self.value = 10
         else: # throw an exception if the input is invalid
            raise Exception("Invalid card value in bjcard.py")
   
   # to string method
   def __str__(self):
      return str(self.face) + self.suit

class Deck():
    """
    A class representing a deck of playing cards, initially ordered.
    Cards are dealt by an index value which moves through the list; shuffling reorders the list
    and resets the index.
    """
    
    
    def __init__(self):
        """
        Creates a new deck.
        """
        self.deck = []
        self.index = 0
        for s in ["S", "H", "D", "C"]:
            for f in ["A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K"]:
                self.deck.append(Card(f, s))

    
    def shuffle(self):
        """
        Reorders the list of cards and resets the index.
        """
        self.index = 0
        newDeck = []
        while len(self.deck) > 0:
            card = self.deck[random.randint(0, len(self.deck) - 1)]
            newDeck.append(card)
            self.deck.remove(card)
        self.deck = newDeck
    		
	
    def drawCard(self):
        """
        Draws the top card, increments the index, and reshuffles if necessary.
        Note: This means it is possible to draw the same card twice, in extremely rare cases.
        """
        if self.index >= len(self.deck) - 1:
            self.shuffle()
        card = self.deck[self.index]
        self.index += 1
        return card

    
    def printDeck(self):
        """
        Test function. Prints out the deck to the console.
        """
        for c in self.deck:
            print(c)
