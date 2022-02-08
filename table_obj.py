import re
import random
from subtable_constants import *


class STTable:

   def __init__(self):
      self.name = "UNNAMED TABLE"
      self.list = []
   
   
   def add(self, entry):
      # add using appropriate method for single or multiple entries
      if re.search("\n", entry):
         self._add_list(entry)
      else:
         self._add_single(entry)
   
   def _add_single(self, entry):
      """ Add a string, which may be a name, entry, or subtable call """
      # ignore empty strings
      if len(entry.strip()) == 0:
         return
      # set table name if name
      if re.search(title_regex, entry):
         self.name = entry[1:]
      # ignore comments, otherwise add
      elif not re.search(comment_regex, entry):
         self.list.append(entry)
   
   
   def _add_list(self, entries):
      """ Add a list of entries """
      line_list = entries.split("\n")
      for element in line_list:
         self.add(element)
   
   
   def roll(self):
      """ Return a random entry from the table """
      if len(self.list) == 0:
         return "[NO ENTRIES]"
      return random.sample(self.list, 1)[0]
   
   
   def dump(self):
      """ Testing/debug method """
      print(self.name)
      if len(self.list) == 0:
         print("[NO ENTRIES]")
      for item in self.list:
         print(item)
   
   
   def summary(self):
      """ Testing/debug method """
      print(self.name)
      print("Entries: {}".format(len(self.list)))


if __name__ == "__main__":
   test_table = STTable()
   print("- Initial state")
   test_table.dump()
   test_table.add("#NAME ONE\nEntry 1\nEntry 2\nEntry 3\n// comment\nEntry 4\n\n")
   test_table.add("Entry 5\n#NAME TWO")
   print("\n- new state")
   test_table.dump()
   print("\n- Random rolls")
   print(test_table.roll())
   print(test_table.roll())
   print(test_table.roll())