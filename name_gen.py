import random

STARTING_CHAR = "@"
ENDING_CHAR = "#"

class NameList:
   """Simple struct for holding two lists."""
   def __init__(self, listA, listB):
      self.listA = listA
      self.listB = listB
   
   def isCompoundList(self):
      if self.listB == None:
         return False
      return True

class MarkovNode:
   """Node for a BST implementation of Markov chains. Expects 3 character chains"""
   def __init__(self, str):
      self.foreStr = str[0:2]
      self.aftStrList = []
      self.aftStrList.append(str[2])
      self.left = None
      self.right = None
   
   def insert(self, str):
      """Insert a 3-character string into the tree"""
      if str[0:2] < self.foreStr:
         if self.left is None:
            self.left = MarkovNode(str)
         else:
            self.left.insert(str)
      elif str[0:2] > self.foreStr:
         if self.right is None:
            self.right = MarkovNode(str)
         else:
            self.right.insert(str)
      else:       # matches
         self.aftStrList.append(str[2])
   
   def retreive(self, str):
      """Get end of a random chain who's first two match the last two of the passed string"""
      if str[1:3] == self.foreStr:
         return random.choice(self.aftStrList)
      if str[1:3] < self.foreStr:
         return self.left.retreive(str)
      else:
         return self.right.retreive(str)

class MarkovNameGen:
   """Master class for Markovian generation"""
   def __init__(self, nameList):
      self.root = None
      self.startingChains = []
      for element in nameList.listA:
         self.addWord(element)
   
   def addWord(self, word):
      global STARTING_CHAR
      global ENDING_CHAR
      word = STARTING_CHAR + word + ENDING_CHAR
      self.startingChains.append(word[0:3])
      if self.root == None:
         self.root = MarkovNode(word[0:3])
      else:
         self.root.insert(word[0:3])
      for i in range(1, len(word) - 2):
         self.root.insert(word[i:i + 3])
   
   def generate(self):
      global STARTING_CHAR
      global ENDING_CHAR
      word = random.choice(self.startingChains)
      while ENDING_CHAR not in word:
         word += self.root.retreive(word[-3:])
      return word[1:-1]

class CompoundNameGen:
   """Master class for compound generation"""
   def __init__(self, nameList):
      self.list = nameList
   
   def generate(self):
      return random.choice(self.list.listA) + random.choice(self.list.listB)


def read_file(file_name):
   "returns file contents in a NameList"
   outList = None
   try:
      rawList = open(file_name, "r").read().split();
      outList = NameList(rawList[1:], None) #MARKOV
      if rawList[0] == "COMPOUND":
         breakLine = -1
         for i in range(0, len(rawList)):
            if rawList[i] == "BREAK":
               breakLine = i
               break
         outList = NameList(rawList[1:breakLine], rawList[breakLine + 1:])
      return outList
   except:
      return None
   return outList

if __name__ == "__main__":
   foreList = read_file("name_dwarf_male.txt")
   surList = read_file("name_dwarf_surname.txt")
   print("foreList:")
   for element in foreList.listA:
      print(" {}".format(element))
   print("surList A:")
   for element in surList.listA:
      print(" {}".format(element))
   print("surList B:")
   for element in surList.listB:
      print(" {}".format(element))
   surGen = CompoundNameGen(surList)
   print("Some random surnames:")
   for i in range(0, 10):
      print(" {}".format(surGen.generate()))
   foreGen = MarkovNameGen(foreList)
   print("Some random forenames:")
   for i in range(0, 10):
      print(" {}".format(foreGen.generate()))
   