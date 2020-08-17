class NameList:
   def __init__(self, listA, listB):
      self.listA = listA
      self.listB = listB
   
   def isCompoundList(self):
      if self.listB == None:
         return False
      return True

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

def generate_names(race, gender):
   return ""

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
   