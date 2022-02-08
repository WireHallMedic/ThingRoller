#!/usr/bin/env python

import sys
import re
from subtable_constants import *
from table_obj import *

class TableController:

   def __init__(self, str):
      """ Instantiate an object. Try and load str as a file name, else treat as file contents. """
      content_string = ""
      try:
         content_string = open(str, "r").read()
      except Exception as ex:
         content_string = str
      
      # trim input to start at first table name
      line_list = content_string.split("\n")
      i = 0
      while not re.search(title_regex, line_list[i]):
         i += 1
      line_list = line_list[i:]
      
      self.table_dict = {}
      # create and populate individual tables
      for line in line_list:
         if re.search(title_regex, line):
            input_table = STTable()
            if len(self.table_dict) == 0:
               self.main_table = input_table
            self.table_dict[line[1:]] = input_table
         input_table.add(line)
   
   
   def roll(self):
      """ Main calling method. Generates an entry from the master list, then 
      fills in the subcalls.
      """
      out_str = self._get_initial_string()
      out_str = self._replace_table_calls(out_str)
      return out_str
   
   
   def _get_initial_string(self):
      if len(self.table_dict) == 0:
         return "EMPTY DICTIONARY"
      return self.main_table.roll()
   
   
   def _get_table(self, str):
      """ Get the table with matching name """
      str = self._clean_table_name(str)
      if str in self.table_dict:
         return self.table_dict[str]
      return "NO TABLE NAMED '{}' EXISTS".format(str)
   
   
   def _clean_table_name(self, str):
      str = str.replace("[", "")
      str = str.replace("]", "")
      str = str.replace("#", "")
      return str
   
   
   def _replace_table_calls(self, str):
      """ 
      Replaces the first instance of a subtable call with an entry from that table.
      Recursively calls self until no more subtable calls are found.
      """
      match = re.search(subtable_call_regex, str)
      if match is not None:
         # extract matching string
         new_str = self._get_replacement(match.group())
         str = str.replace(match.group(), new_str, 1)
         return self._replace_table_calls(str)
      return str
   
   
   def _get_replacement(self, substring):
      """ Returns an entry from the specified subtable """
      table = self._get_table(substring)
      if isinstance(table, str):
         return table
      return table.roll()
   
   
   def dump(self):
      """ Testing and debugging method """
      print("Number of tables: {}".format(len(self.table_dict)))
      for key in self.table_dict:
         print()
         self._get_table(key).dump()
   
   
   def summary(self):
      """ Testing and debugging method """
      print("Number of tables: {}".format(len(self.table_dict)))
      for key in self.table_dict:
         print()
         self._get_table(key).summary()
      

if __name__ == "__main__":
   if len(sys.argv) == 1:
      test = TableController("TestText.txt")
      print(test.roll())
   else:
      table = TableController(sys.argv[1])
      for i in range(5):
         print(table.roll())
   