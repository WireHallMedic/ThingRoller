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
      """Get a random chain who's first two match the last two of the passed string"""
      if str[1:3] == self.foreStr:
         return self.foreStr + random.choice(self.aftStrList)
      if str[1:3] < self.foreStr:
         return self.left.retreive(str)
      else
         return self.right.retreive(str)

class MarkovNameGen:
   """Master class for Markovian generation"""
   def __init__(self):
      self.root = None
      self.startingChains = []

class CompoundNameGen:
   """Master class for compound generation"""
   def __init__(self, fileName):
      pass

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
   