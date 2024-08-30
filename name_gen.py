import random

STARTING_CHAR = "@"
ENDING_CHAR = "#"
MIN_MARKOV_NAME_LEN = 4
MAX_MARKOV_NAME_LEN = 12   # some name styles may have custom max lengths

class NameList:
   """Simple struct for holding two lists."""
   def __init__(self, list_a, list_b):
      self.list_a = list_a
      self.list_b = list_b
      for element in self.list_a:
         element = element.lower()
      if self.list_b is not None:
         for element in self.list_b:
            element = element.lower()
   
   def is_compound_list(self):
      """Returns true if list is formatted for A+B generation, else false"""
      if self.list_b == None:
         return False
      return True
   
   def is_markov_list(self):
      """Returns true if list is formatted for Markov generation, else false"""
      return not self.is_compound_list()

class MarkovNode:
   """Node for a BST implementation of Markov chains. Expects 3 character chains"""
   def __init__(self, str):
      self.fore_str = str[0:2]
      self.aft_str_list = []
      self.aft_str_list.append(str[2])
      self.left = None
      self.right = None
   
   def insert(self, str):
      """Insert a 3-character string into the tree"""
      if str[0:2] < self.fore_str:
         if self.left is None:
            self.left = MarkovNode(str)
         else:
            self.left.insert(str)
      elif str[0:2] > self.fore_str:
         if self.right is None:
            self.right = MarkovNode(str)
         else:
            self.right.insert(str)
      else:       # matches
         self.aft_str_list.append(str[2])
   
   def retreive(self, str):
      """Get end of a random chain who's first two match the last two of the passed string"""
      if str[1:3] == self.fore_str:
         return random.choice(self.aft_str_list)
      if str[1:3] < self.fore_str:
         return self.left.retreive(str)
      else:
         return self.right.retreive(str)

class MarkovNameGen:
   """Master class for Markovian generation"""
   def __init__(self, name_list, min = None, max = None):
      global MIN_MARKOV_NAME_LEN
      global MAX_MARKOV_NAME_LEN
      self.min_len = MIN_MARKOV_NAME_LEN
      self.max_len = MAX_MARKOV_NAME_LEN
      if min != None:
         self.min_len = min
      if max != None:
         self.max_len = max
      self.root = None
      self.starting_chains = []
      for element in name_list.list_a:
         self.add_word(element)
   
   def add_word(self, word):
      """Add a word's components to the tree"""
      global STARTING_CHAR
      global ENDING_CHAR
      word = STARTING_CHAR + word + ENDING_CHAR
      self.starting_chains.append(word[0:3])
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
      good_length = False
      while good_length == False:
         word = random.choice(self.starting_chains)
         while ENDING_CHAR not in word:
            word += self.root.retreive(word[-3:])
         out_word = word[1:-1] # strip control characters
         if len(out_word) >= self.min_len and len(out_word) <= self.max_len:
            good_length = True
      return format_output(out_word)


class CompoundNameGen:
   """Master class for compound generation"""
   def __init__(self, name_list):
      self.list = name_list
   
   def generate(self):
      out_str = random.choice(self.list.list_a) + random.choice(self.list.list_b)
      return format_output(out_str)

class SampleNameGen:
   """Master class for sampling names from list rather than generating"""
   def __init__(self, name_list):
      self.list = name_list
   
   def generate(self):
      return format_output(random.choice(self.list))

def format_output(str):
   """Make it pretty"""
   out_str = str.replace("_", " ")
   out_str = str.capitalize()
   return out_str

def read_file(file_name):
   """Returns file contents in a NameList"""
   out_list = None
   try:
      raw_list = open(file_name, "r").read().split();
      out_list = None
      if raw_list[0] == "MARKOV":
         out_list = NameList(raw_list[1:], None)
      elif raw_list[0] == "COMPOUND":
         break_line = -1
         for i in range(0, len(raw_list)):
            if raw_list[i] == "BREAK":
               break_line = i
               break
         out_list = NameList(raw_list[1:break_line], raw_list[break_line + 1:])
      else:
         print("No recognized format in file {}".format(file_name))
      return out_list
   except:
      return None
   return out_list

def generator_generator(file_name, min = None, max = None):
   """Create a Markov generator for the passed text file"""
   name_list = read_file(file_name)
   if name_list.is_compound_list():
      return CompoundNameGen(name_list)
   return MarkovNameGen(name_list, min, max)

if __name__ == "__main__":
   """
   foreList = read_file("name_dwarf_male.txt")
   surList = read_file("name_dwarf_surname.txt")
   print("foreList:")
   for element in foreList.list_a:
      print(" {}".format(element))
   print("surList A:")
   for element in surList.list_a:
      print(" {}".format(element))
   print("surList B:")
   for element in surList.list_b:
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
   fore_name_gen = generator_generator("name_european_male.txt")
   sur_name_gen = generator_generator("name_european_surname.txt")
   for i in range(0, 10):
      print("{} {}".format(fore_name_gen.generate(), sur_name_gen.generate()))
   