

import random

class QuestGenerator:
   def __init__(self, fileName):
      self.verbList = []
      self.subjectList = []
      self.placeList = []
      self.hindranceList = []
      self.antagonistList = []
      self.listDict = {
         "@VERB":self.verbList,
         "@SUBJECT":self.subjectList,
         "@PLACE":self.placeList,
         "@HINDRANCE":self.hindranceList,
         "@ANTAGONIST":self.antagonistList}
      self._readFile(fileName)
   
   def generate(self):
      return "The adventurers must {} the {} in the {}, while dealing with {} and opposing the {}.".format(
         random.choice(self.verbList),
         random.choice(self.subjectList),
         random.choice(self.placeList),
         random.choice(self.hindranceList),
         random.choice(self.antagonistList))
   
   def _readFile(self, fileName):
      """Load the lists"""
      curList = self.verbList
      try:
         rawList = open(fileName, "r").read().split("\n");
         curList = self.verbList
         for str in rawList:
            if str == "":
               # skip blank lines
               continue
            elif str[0] == "@":
               # adjust list when told
               curList = self.listDict[str]
            else:
               # put word in list
               curList.append(str.lower())
      except ex:
         print("Unable to parse file {} because {}".format(fileName, ex))

if __name__ == "__main__":
   gen = QuestGenerator("questparts.txt")
   print(gen.generate())
   print(gen.generate())
   print(gen.generate())