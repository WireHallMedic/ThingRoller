import random

HEART_CHAR = ":hearts:"
DIAMOND_CHAR  = ":diamonds:"
SPADE_CHAR  = ":spades:"
CLUB_CHAR  = ":clubs:"
JOKER_CHAR = "!"

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
      if s == "H" or s == "S" or s == "D" or s == "C" or s == JOKER_CHAR:
         self.suit = s
         """
      if s == "H":
         self.suit = HEART_CHAR
      elif s == "S":
         self.suit = SPADE_CHAR
      elif s == "D":
         self.suit = DIAMOND_CHAR
      elif s == "C":
         self.suit = CLUB_CHAR"""
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
         elif self.face == JOKER_CHAR:
            self.value = 0
         else: # throw an exception if the input is invalid
            raise Exception("Invalid card value in bjcard.py")
   
   # to string method
   def __str__(self):
      if self.is_joker():
         if self.suit == "H":
            return "Joker (red)"
         else:
            return "Joker (black)"
      return str(self.face) + self.suit
      
   # is this card a joker
   def is_joker(self):
      return self.face == JOKER_CHAR

class Deck():
    """
    A class representing a deck of playing cards, initially ordered.
    Cards are dealt by an index value which moves through the list; shuffling reorders the list
    and resets the index.
    """
    
    def __init__(self, has_jokers = False):
        self._new_deck(has_jokers)
    
    def _new_deck(self, has_jokers):
        """
        Creates a new deck.
        """
        self.deck = []
        self.index = 0
        self.jokers = has_jokers
        for s in ["S", "H", "D", "C"]:
            for f in ["A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K"]:
                self.deck.append(Card(f, s))
        if self.jokers:
            self.deck.append(Card(JOKER_CHAR, "H"))
            self.deck.append(Card(JOKER_CHAR, "S"))
    
    def shuffle(self, has_jokers = None):
        """
        Reorders the list of cards and resets the index.
        """
        if has_jokers != None and has_jokers != self.jokers:
            self._new_deck(has_jokers)
        self.index = 0
        new_deck = []
        while len(self.deck) > 0:
            card = self.deck[random.randint(0, len(self.deck) - 1)]
            new_deck.append(card)
            self.deck.remove(card)
        self.deck = new_deck
	 
    def draw_card(self):
        """
        Draws the top card, increments the index, and reshuffles if necessary.
        Note: This means it is possible to draw the same card twice, in extremely rare cases.
        """
        if self.index >= len(self.deck) - 1:
            self.shuffle()
        card = self.deck[self.index]
        self.index += 1
        return card
    
    def print_deck(self):
        """
        Test function. Prints out the deck to the console.
        """
        for c in self.deck:
            print(c)

""" Test functions """
if __name__ == "__main__":
   deck = Deck()
   deck = Deck(False)
   deck.print_deck()
   deck.shuffle(True)
   deck.print_deck()