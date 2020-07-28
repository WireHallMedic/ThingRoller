import discord
import json
import re
import random

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

# let's load some things from files
token = open("token.txt", "r").read()
msgDict = json.loads(open("messages.json","r").read())
tavernSuffixes = open("tavernSuffixes.txt", "r").read().split("\n");
tavernForename = open("tavernForenames.txt", "r").read().split("\n");
tavernSurname = open("tavernSurnames.txt", "r").read().split("\n");
interludes = open("interludes.txt", "r").read().split("\n");

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
      outStr = genTavern(intArg)
      
   # roll interlude
   if cmd == "interlude":
      outStr = genInterlude()
   
   #roll some dice and/or calculate
   if re.search(shouldCalcRegEx, cmd) != None:
      outStr = resolveDiceExpr(cmd.replace("*", "x"))
      if outStr == None:
         outStr = msgDict["parsingFailure"].format(cmd)
   
   if outStr != None:
      await message.channel.send(outStr)

def cleanMessage(str):
   newStr = str[1:]
   newStr = newStr.lower()
   newStr = newStr.strip()
   return newStr

def genTavern(reps):
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

def genInterlude():
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

# fire this bad boy up
client.run(token)

# {message.channel}: {message.author}: {message.author.name}: {message.content}