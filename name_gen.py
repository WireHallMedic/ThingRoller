import random

STARTING_CHAR = "@"
ENDING_CHAR = "#"
MIN_MARKOV_NAME_LEN = 4
MAX_MARKOV_NAME_LEN = 12   # some name styles may have custom max lengths

class NameList:
   """Simple struct for holding two lists."""
   def __init__(self, listA, listB):
      self.listA = listA
      self.listB = listB
      for element in self.listA:
         element = element.lower()
      if self.listB is not None:
         for element in self.listB:
            element = element.lower()
   
   def isCompoundList(self):
      """Returns true if list is formatted for A+B generation, else false"""
      if self.listB == None:
         return False
      return True
   
   def isMarkovList(self):
      """Returns true if list is formatted for Markov generation, else false"""
      return not self.isCompoundList()

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
   def __init__(self, nameList, min = None, max = None):
      global MIN_MARKOV_NAME_LEN
      global MAX_MARKOV_NAME_LEN
      self.minLen = MIN_MARKOV_NAME_LEN
      self.maxLen = MAX_MARKOV_NAME_LEN
      if min != None:
         self.minLen = min
      if max != None:
         self.maxLen = max
      self.root = None
      self.startingChains = []
      for element in nameList.listA:
         self.addWord(element)
   
   def addWord(self, word):
      """Add a word's components to the tree"""
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
      """Generate a word using the tree"""
      global STARTING_CHAR
      global ENDING_CHAR
      goodLength = False
      while goodLength == False:
         word = random.choice(self.startingChains)
         while ENDING_CHAR not in word:
            word += self.root.retreive(word[-3:])
         outWord = word[1:-1] # strip control characters
         if len(outWord) >= self.minLen and len(outWord) <= self.maxLen:
            goodLength = True
      return formatOutput(outWord)


class CompoundNameGen:
   """Master class for compound generation"""
   def __init__(self, nameList):
      self.list = nameList
   
   def generate(self):
      outStr = random.choice(self.list.listA) + random.choice(self.list.listB)
      return formatOutput(outStr)

def formatOutput(str):
   """Make it pretty"""
   outStr = str.replace("_", " ")
   outStr = str.capitalize()
   return outStr

def readFile(fileName):
   """Returns file contents in a NameList"""
   outList = None
   try:
      rawList = open(fileName, "r").read().split();
      outList = None
      if rawList[0] == "MARKOV":
         outList = NameList(rawList[1:], None)
      elif rawList[0] == "COMPOUND":
         breakLine = -1
         for i in range(0, len(rawList)):
            if rawList[i] == "BREAK":
               breakLine = i
               break
         outList = NameList(rawList[1:breakLine], rawList[breakLine + 1:])
      else:
         print("No recognized format in file {}".format(fileName))
      return outList
   except:
      return None
   return outList

def generatorGenerator(fileName, min = None, max = None):
   """Create a Markov generator for the passed text file"""
   nameList = readFile(fileName)
   if nameList.isCompoundList():
      return CompoundNameGen(nameList)
   return MarkovNameGen(nameList, min, max)

if __name__ == "__main__":
   """
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
   """
   foreNameGen = generatorGenerator("name_european_male.txt")
   surNameGen = generatorGenerator("name_european_surname.txt")
   for i in range(0, 10):
      print("{} {}".format(foreNameGen.generate(), surNameGen.generate()))
   