import discord
import json
import re
import os
import random
import name_gen
import deck
import socket
import subtable_main

# various regExes
diceRegEx = "\d+d\d+|advantage|disadvantage"
intRegEx = "\d+"
opRegEx = "[+\-/*x]"
nonOpRegEx = "[^+\-/\*x]"
shouldCalcRegEx = "^[+\-\d]|^d\d|^advantage|^disadvantage"
shouldInsertOne = "^d\d"
numberRegEx = "\d+"

notYetImplementedStr = ":warning: This feature is not yet implemented :warning:"
MAX_DICE = 1000000
adminName = "wire_hall_medic"

# change cwd in case this is called from shell script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# let's load some things from files
token = open("token.txt", "r").read()
msgDict = json.loads(open("json_files/messages.json","r").read())
relicDict = json.loads(open("json_files/relicDescription.json","r").read())
tavernSuffixes = open("text_files/tavernSuffixes.txt", "r").read().split("\n")
tavernForename = open("text_files/tavernForenames.txt", "r").read().split("\n")
tavernSurname = open("text_files/tavernSurnames.txt", "r").read().split("\n")
interludes = open("text_files/interludes.txt", "r").read().split("\n")

# load name generations
nameDict = {}
nameDict["dragonborn_female"] = name_gen.generatorGenerator("text_files/name_dragonborn_female.txt", max = 20)
nameDict["dragonborn_male"] = name_gen.generatorGenerator("text_files/name_dragonborn_male.txt", max = 20)
nameDict["dragonborn_surname"] = name_gen.generatorGenerator("text_files/name_dragonborn_surname.txt")
nameDict["dwarf_female"] = name_gen.generatorGenerator("text_files/name_dwarf_female.txt")
nameDict["dwarf_male"] = name_gen.generatorGenerator("text_files/name_dwarf_male.txt")
nameDict["dwarf_surname"] = name_gen.generatorGenerator("text_files/name_dwarf_surname.txt")
nameDict["elf_female"] = name_gen.generatorGenerator("text_files/name_elf_female.txt")
nameDict["elf_male"] = name_gen.generatorGenerator("text_files/name_elf_male.txt")
nameDict["elf_surname"] = name_gen.generatorGenerator("text_files/name_elf_surname.txt")
nameDict["european_female"] = name_gen.generatorGenerator("text_files/name_european_female.txt")
nameDict["european_male"] = name_gen.generatorGenerator("text_files/name_european_male.txt")
nameDict["european_surname"] = name_gen.generatorGenerator("text_files/name_european_surname.txt")
nameDict["gnome_female"] = name_gen.generatorGenerator("text_files/name_gnome_female.txt")
nameDict["gnome_male"] = name_gen.generatorGenerator("text_files/name_gnome_male.txt")
nameDict["gnome_surname"] = name_gen.generatorGenerator("text_files/name_gnome_surname.txt")
nameDict["halfling_female"] = name_gen.generatorGenerator("text_files/name_halfling_female.txt")
nameDict["halfling_male"] = name_gen.generatorGenerator("text_files/name_halfling_male.txt")
nameDict["halfling_surname"] = name_gen.generatorGenerator("text_files/name_halfling_surname.txt")
nameDict["orc_female"] = name_gen.generatorGenerator("text_files/name_orc_female.txt")
nameDict["orc_male"] = name_gen.generatorGenerator("text_files/name_orc_male.txt")
nameDict["angel"] = name_gen.generatorGenerator("text_files/name_angel.txt")
nameDict["demon"] = name_gen.generatorGenerator("text_files/name_demon.txt")
nameDict["dragon"] = name_gen.generatorGenerator("text_files/name_dragon.txt", min = 8, max = 20)

#everone loves lists
relicCreator = []
relicHistory = []
relicMinorProp = []
relicQuirk = []

for key in relicDict["creator"]:
      relicCreator.append(relicDict["creator"][key])
for key in relicDict["history"]:
      relicHistory.append(relicDict["history"][key])
for key in relicDict["minor"]:
      relicMinorProp.append(relicDict["minor"][key])
for key in relicDict["quirk"]:
      relicQuirk.append(relicDict["quirk"][key])

# deck of cards
deck = deck.Deck(has_jokers = False)
deck.shuffle()

# table-based generators

kung_fu_generator = subtable_main.TableController("text_files/kung_fu.txt")
quest_generator = subtable_main.TableController("text_files/quest_parts.txt")

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')
    
@client.event
async def on_message(message):
   # don't respond to self, empty messages, or things that don't start with a bang
   if message.author == client.user or \
      len(message.content) == 0 or \
      message.content[0] != "!":
      return
   
   # we've got a potential command, format it
   cmd = cleanMessage(message.content)
   intArg = 0
   outStr = None
   
   # extract any integer argument passed in
   if re.search(intRegEx, cmd) != None:
      intArg = int(re.search(intRegEx, cmd)[0])
   
   # bot info
   if cmd == "thingroller":
      outStr = msgDict["botInfo"]
      for key in msgDict["recognizedCommands"]:
         outStr += "\n  " + key + " " + msgDict["recognizedCommands"][key]
      outStr += "\n" + msgDict["commandNotes"]
   elif cmd == "status":
      outStr = msgDict["goodStatus"]
      addr = getIPAddress()
      outStr = "{}\nHostname: {}\nIP Address: {}".format(outStr, addr[0], addr[1]);
      
   # dice expression examples
   if cmd == "examples":
      outStr = "__Examples of Things I Can Calculate__:\n"
      outStr += msgDict["formatExamples"] + "\n"
      outStr += msgDict["formatNotes"]
      
   # stat block
   if cmd == "stat block":
      outStr = rollStatBlock()
      
   # roll tavern
   if re.search("^tavern", cmd):
      outStr = generateTavern(intArg)
   
   if re.search("^kung fu", cmd):
      outStr = generateKungFu(intArg)
      
   # roll interlude
   if cmd == "interlude":
      outStr = generateInterlude()
   
   #roll some dice and/or calculate
   if re.search(shouldCalcRegEx, cmd) != None:
      outStr = resolveDiceExpr(cmd.replace("*", "x"))
      if outStr == None:
         outStr = msgDict["parsingFailure"].format(cmd)
   
   #relic generator
   if cmd == "relic":
      outStr = generateRelic()
   
   #draw cards
   if re.search("^draw", cmd):
      num_to_draw = max(1, intArg)
      num_to_draw = min(52, num_to_draw)
      outStr = ""
      for i in range(num_to_draw):
         outStr = outStr + str(deck.drawCard()) + " "
   
   #generate quests
   if re.search("^quest", cmd):
      num_of_quests = max(1, intArg)
      num_of_quests = min(5, num_of_quests)
      outStr = ""
      for i in range(num_of_quests):
         outStr = outStr + quest_generator.roll() + "\n"
      outStr = outStr.strip()
   
   #shuffle cards
   if cmd == "shuffle":
      deck.shuffle()
      outStr = "Deck reshuffled"
   if cmd == "shuffle jokers" or cmd == "jokers":
      deck.shuffle(True)
      outStr = "Deck reshuffled (jokers included)"
   if cmd == "shuffle no jokers" or cmd == "no jokers":
      deck.shuffle(False)
      outStr = "Deck reshuffled (jokers excluded)"
   
   # name generator
   if re.search("^name", cmd):
      outStr = generateNames(cmd, intArg)
   
   if outStr != None:
      await message.channel.send(outStr)

def cleanMessage(str):
   newStr = str[1:]
   newStr = newStr.lower()
   newStr = newStr.strip()
   return newStr

def generateTavern(reps):
   reps = max(1, reps)
   reps = min(20, reps)
   str = ""
   for i in range(reps):
      str += "The "
      str += random.choice(tavernForename) + " "
      str += random.choice(tavernSurname) + " "
      str += random.choice(tavernSuffixes) + "\n"
   str = str.strip()
   return str;

def resolveDiceExpr(diceExpr):
   try:
      # strip out spaces
      diceExpr = diceExpr.replace(" ", "")
      # if it starts with a negative number or expression, put in a zero
      if diceExpr[0] == "-":
         diceExpr = "0" + diceExpr
      # make lists of expressions and operators
      exprList = re.split(opRegEx, diceExpr)
      opList = re.findall(opRegEx, diceExpr)
      # resolve expressions
      valList = []
      for val in exprList:
         valList.append(resolveSingleDiceExpr(val))
      # resolve operators
      sum = resolveAllOperators(valList, opList);
      # compile output
      outStr = f'**Result: {sum}**\n'
      outStr += "Rolled: "
      outStr += valList[0][1]
      for i in range(1, len(valList)):
         outStr += " " + opList[i - 1] + " " + valList[i][1]
      return outStr
   except:
      return None

def resolveSingleDiceExpr(diceExpr):
   try:
      # handle advantage and disadvantage
      if diceExpr == "advantage":
         return resolveAdvantage()
      if diceExpr == "disadvantage":
         return resolveDisadvantage()
      
      val = [0, diceExpr]
      # handle raw numbers
      if re.search("d", diceExpr) == None:
         val[0] = int(diceExpr)
         return val
      
      # handle dice
      diceExpr = diceExpr.split("d")
      iterations = int(diceExpr[0])
      if iterations > MAX_DICE:
         return None
      for i in range(iterations):
         val[0] += roll(int(diceExpr[1]))
      val[1] = f'{val[0]}'
      return val
   except:
      return None

def resolveAdvantage():
   a = roll(20)
   b = roll(20)
   val = [0, ""]
   val[0] = max(a, b)
   val[1] = f'max({a}, {b})'
   return val

def resolveDisadvantage():
   a = roll(20)
   b = roll(20)
   val = [0, ""]
   val[0] = min(a, b)
   val[1] = f'min({a}, {b})'
   return val

def roll(val):
   return random.randint(1, val)

def generateInterlude():
   return random.choice(interludes)

def resolveAllOperators(valList, opList):
   try:
      sum = valList[0][0];
      valIndex = 1
      while valIndex < len(valList):
         sum = resolveSingleOperator(sum, valList[valIndex][0], opList[valIndex - 1])
         valIndex += 1
      return sum
   except:
      return None

def resolveSingleOperator(sum, val, op):
   if op == "+":
      return sum + val
   elif op == "-":
      return sum - val
   elif op == "/":
      return sum / val
   elif op == "x" or op == "*":
      return sum * val
   return None

def rollStatBlock():
   stat = []
   rolledStr = []
   for i in range(8):
      rollArr = rollSingleStat()
      sum = rollArr[0] + rollArr[1] + rollArr[2] + rollArr[3] - min(rollArr)
      rolledStr.append(f'{sum} ({rollArr[0]}, {rollArr[1]}, {rollArr[2]}, {rollArr[3]})')
      stat.append(sum)
   stat.sort(reverse=True)
   stat = stat[0:-2]
   outStr = "**Results : "
   for i in range(0, 6):
      outStr += f'{stat[i]}'
      if i < 5:
         outStr += ", "
      else:
         outStr += "**"
   for element in rolledStr:
      outStr += "\n  " + element
   return outStr

def rollSingleStat():
   return [roll(6), roll(6), roll(6), roll(6)]

def generateKungFu(reps):
   reps = max(1, reps)
   reps = min(20, reps)
   outStr = ""
   for i in range(reps):
      outStr = "{}\n{}".format(outStr, kung_fu_generator.roll())
   return outStr

def generateNames(cmd, intArg):
   strList = cmd.split()
   strList.append("")   # beacuse not everything needs a gender
   reps = 5
   if intArg != 0:
      reps = intArg
   reps = max(1, reps)
   reps = min(20, reps)
   outStr = ""
   try:
      for i in range(0, reps):
         outStr += getSingleName(strList[1], strList[2]) + "\n"
      outStr = outStr[:-1] # trim the last newline
      return outStr
   except:
      return msgDict["nameParsingFailure"].format(cmd)

def getSingleName(race, sex):
   if race == "dragonborn":
      if sex == "female":
         return "{} {}".format(nameDict["dragonborn_female"].generate(), nameDict["dragonborn_surname"].generate())
      elif sex == "male":
         return "{} {}".format(nameDict["dragonborn_male"].generate(), nameDict["dragonborn_surname"].generate())
   elif race == "dwarf":
      if sex == "female":
         return "{} {}".format(nameDict["dwarf_female"].generate(), nameDict["dwarf_surname"].generate())
      elif sex == "male":
         return "{} {}".format(nameDict["dwarf_male"].generate(), nameDict["dwarf_surname"].generate())
   elif race == "elf":
      if sex == "female":
         return "{} {}".format(nameDict["elf_female"].generate(), nameDict["elf_surname"].generate())
      elif sex == "male":
         return "{} {}".format(nameDict["elf_male"].generate(), nameDict["elf_surname"].generate())
   elif race == "european":
      if sex == "female":
         return "{} {}".format(nameDict["european_female"].generate(), nameDict["european_surname"].generate())
      elif sex == "male":
         return "{} {}".format(nameDict["european_male"].generate(), nameDict["european_surname"].generate())
   elif race == "gnome":
      if sex == "female":
         return "{} {}".format(nameDict["gnome_female"].generate(), nameDict["gnome_surname"].generate())
      elif sex == "male":
         return "{} {}".format(nameDict["gnome_male"].generate(), nameDict["gnome_surname"].generate())
   elif race == "halfling":
      if sex == "female":
         return "{} {}".format(nameDict["halfling_female"].generate(), nameDict["halfling_surname"].generate())
      elif sex == "male":
         return "{} {}".format(nameDict["halfling_male"].generate(), nameDict["halfling_surname"].generate())
   elif race == "orc":
      if sex == "female":
         return nameDict["orc_female"].generate()
      elif sex == "male":
         return nameDict["orc_male"].generate()
   elif race == "angel":
      return nameDict["angel"].generate()
   elif race == "demon":
      return nameDict["demon"].generate()
   elif race == "dragon":
      return nameDict["dragon"].generate()
   print("bad name request {} {}".format(race, sex))
   raise Exception("bad name request {} {}".format(race, sex))
   return None

# stuff for relic generation
def getCreator():
   return random.choice(relicCreator)

def getHistory():
   return random.choice(relicHistory)

def getQuirk():
   return random.choice(relicQuirk)

def getMinorProp():
   outStr1 = random.choice(relicMinorProp)
   outStr2 = ""
   if outStr1 == "ROLL_TWICE":
      outStr2 = random.choice(relicMinorProp)
   while outStr1 == "ROLL_TWICE":
      outStr1 = random.choice(relicMinorProp)
   while outStr2 == outStr1 or outStr2 == "ROLL_TWICE":
      outStr2 = random.choice(relicMinorProp)
   if outStr2 != "":
      outStr1 += "\n"
   return outStr1 + outStr2

def generateRelic():
   return relicDict["format"].format(getCreator(), getHistory(), getMinorProp(), getQuirk())

def getIPAddress():
   vals = ["", ""]
   addr = ["Unable to get hostname", "Unable to get IP"]
   try:
      addr[0] = socket.gethostname()
   except:
      addr[0] = "Unable to get hostname"
   try:
      addr[1] = socket.gethostbyname(addr[0] + ".local")
   except:
      addr[1] = "Unable to get IP address"
   return addr

# fire this bad boy up
client.run(token)

# {message.channel}: {message.author}: {message.author.name}: {message.content}