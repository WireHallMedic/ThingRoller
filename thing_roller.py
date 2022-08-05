import discord
import json
import re
import os
import random
import name_gen
import deck
import dice
import socket
import subtable_main
import constants

# change cwd in case this is called from shell script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# let's load some things from files
token = open("token.txt", "r").read()
message_dict = json.loads(open("json_files/messages.json","r").read())
relic_dict = json.loads(open("json_files/relicDescription.json","r").read())
interludes = open("text_files/interludes.txt", "r").read().split("\n")

# load name generations
name_dict = {}
name_dict["dragonborn_female"] = name_gen.generator_generator("text_files/name_dragonborn_female.txt", max = 20)
name_dict["dragonborn_male"] = name_gen.generator_generator("text_files/name_dragonborn_male.txt", max = 20)
name_dict["dragonborn_surname"] = name_gen.generator_generator("text_files/name_dragonborn_surname.txt")
name_dict["dwarf_female"] = name_gen.generator_generator("text_files/name_dwarf_female.txt")
name_dict["dwarf_male"] = name_gen.generator_generator("text_files/name_dwarf_male.txt")
name_dict["dwarf_surname"] = name_gen.generator_generator("text_files/name_dwarf_surname.txt")
name_dict["elf_female"] = name_gen.generator_generator("text_files/name_elf_female.txt")
name_dict["elf_male"] = name_gen.generator_generator("text_files/name_elf_male.txt")
name_dict["elf_surname"] = name_gen.generator_generator("text_files/name_elf_surname.txt")
name_dict["european_female"] = name_gen.generator_generator("text_files/name_european_female.txt")
name_dict["european_male"] = name_gen.generator_generator("text_files/name_european_male.txt")
name_dict["european_surname"] = name_gen.generator_generator("text_files/name_european_surname.txt")
name_dict["gnome_female"] = name_gen.generator_generator("text_files/name_gnome_female.txt")
name_dict["gnome_male"] = name_gen.generator_generator("text_files/name_gnome_male.txt")
name_dict["gnome_surname"] = name_gen.generator_generator("text_files/name_gnome_surname.txt")
name_dict["halfling_female"] = name_gen.generator_generator("text_files/name_halfling_female.txt")
name_dict["halfling_male"] = name_gen.generator_generator("text_files/name_halfling_male.txt")
name_dict["halfling_surname"] = name_gen.generator_generator("text_files/name_halfling_surname.txt")
name_dict["orc_female"] = name_gen.generator_generator("text_files/name_orc_female.txt")
name_dict["orc_male"] = name_gen.generator_generator("text_files/name_orc_male.txt")
name_dict["angel"] = name_gen.generator_generator("text_files/name_angel.txt")
name_dict["demon"] = name_gen.generator_generator("text_files/name_demon.txt")
name_dict["dragon"] = name_gen.generator_generator("text_files/name_dragon.txt", min = 8, max = 20)

#everone loves lists
relic_creator = []
relic_history = []
relic_minor_prop = []
relic_quick = []

for key in relic_dict["creator"]:
      relic_creator.append(relic_dict["creator"][key])
for key in relic_dict["history"]:
      relic_history.append(relic_dict["history"][key])
for key in relic_dict["minor"]:
      relic_minor_prop.append(relic_dict["minor"][key])
for key in relic_dict["quirk"]:
      relic_quick.append(relic_dict["quirk"][key])

# deck of cards
deck = deck.Deck(has_jokers = False)
deck.shuffle()

# table-based generators
kung_fu_generator = subtable_main.TableController("text_files/kung_fu.txt")
quest_generator = subtable_main.TableController("text_files/quest_parts.txt")
tavern_generator = subtable_main.TableController("text_files/taverns.txt")

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
   int_arg = 0
   out_str = None
   
   # extract any integer argument passed in
   if re.search(INT_REG_EX, cmd) != None:
      int_arg = int(re.search(INT_REG_EX, cmd)[0])
   
   # bot info
   if cmd == "thingroller":
      out_str = message_dict["botInfo"]
      for key in message_dict["recognizedCommands"]:
         out_str += "\n  " + key + " " + message_dict["recognizedCommands"][key]
      out_str += "\n" + message_dict["commandNotes"]
   elif cmd == "status":
      out_str = message_dict["goodStatus"]
      addr = getIPAddress()
      out_str = "{}\nHostname: {}\nIP Address: {}".format(out_str, addr[0], addr[1]);
      
   # dice expression examples
   if cmd == "examples":
      out_str = "__Examples of Things I Can Calculate__:\n"
      out_str += message_dict["formatExamples"] + "\n"
      out_str += message_dict["formatNotes"]
      
   # stat block
   if cmd == "stat block":
      out_str = roll_stat_block()
      
   # roll tavern
   if re.search("^tavern", cmd):
      out_str = generate_tavern(int_arg)
   
   if re.search("^kung fu", cmd):
      out_str = generate_kung_fu(int_arg)
      
   # roll interlude
   if cmd == "interlude":
      out_str = generate_interlude()
      
   # aliases for 4dF
   if cmd == "fudge" or cmd == "fate":
      cmd = "4df"
   
   #roll some dice and/or calculate
   if re.search(SHOULD_CALCULATE_REG_EX, cmd) != None:
      out_str = resolve_dice_expression(cmd.replace("*", "x"))
      if out_str == None:
         out_str = message_dict["parsingFailure"].format(cmd)
   
   #relic generator
   if cmd == "relic":
      out_str = generate_relic()
   
   #draw cards
   if re.search("^draw", cmd):
      num_to_draw = max(1, int_arg)
      num_to_draw = min(52, num_to_draw)
      out_str = ""
      for i in range(num_to_draw):
         out_str = out_str + str(deck.draw_card()) + " "
   
   #generate quests
   if re.search("^quest", cmd):
      num_of_quests = max(1, int_arg)
      num_of_quests = min(5, num_of_quests)
      out_str = ""
      for i in range(num_of_quests):
         out_str = out_str + quest_generator.roll() + "\n"
      out_str = out_str.strip()
   
   #shuffle cards
   if cmd == "shuffle":
      deck.shuffle()
      out_str = "Deck reshuffled"
   if cmd == "shuffle jokers" or cmd == "jokers":
      deck.shuffle(True)
      out_str = "Deck reshuffled (jokers included)"
   if cmd == "shuffle no jokers" or cmd == "no jokers":
      deck.shuffle(False)
      out_str = "Deck reshuffled (jokers excluded)"
   
   # name generator
   if re.search("^name", cmd):
      out_str = generate_names(cmd, int_arg)
   
   if out_str != None:
      await message.channel.send(out_str)

def cleanMessage(str):
   new_str = str[1:]
   new_str = new_str.lower()
   new_str = new_str.strip()
   return new_str

def generate_tavern(reps):
   reps = max(1, reps)
   reps = min(20, reps)
   str = ""
   for i in range(reps):
      str += "{}\n".format(tavern_generator.roll())
   str = str.strip()
   return str;

def resolve_dice_expression(dice_expression):
   try:
      # strip out spaces
      dice_expression = dice_expression.replace(" ", "")
      # if it starts with a negative number or expression, put in a zero
      if dice_expression[0] == "-":
         dice_expression = "0" + dice_expression
      # make lists of expressions and operators
      expression_list = re.split(OPERATOR_REG_EX, dice_expression)
      operator_list = re.findall(OPERATOR_REG_EX, dice_expression)
      # resolve expressions
      val_list = []
      for val in expression_list:
         val_list.append(resolve_single_dice_expression(val))
      # resolve operators
      sum = resolve_all_operators(val_list, operator_list);
      # compile output
      out_str = f'**Result: {sum}**\n'
      out_str += "Rolled: "
      out_str += val_list[0][1]
      for i in range(1, len(val_list)):
         out_str += " " + operator_list[i - 1] + " " + val_list[i][1]
      return out_str
   except:
      return None

def resolve_single_dice_expression(dice_expression):
   try:
      # handle advantage and disadvantage
      if dice_expression == "advantage":
         return resolve_advantage()
      if dice_expression == "disadvantage":
         return resolve_disadvantage()
      
      val = [0, dice_expression]
      # handle raw numbers
      if re.search("d", dice_expression) == None:
         val[0] = int(dice_expression)
         return val
      
      # handle dice
      val[1] = ""
      dice_expression = dice_expression.split("d")
      iterations = int(dice_expression[0])
      result = 0
      if iterations > MAX_DICE:
         return None
      for i in range(iterations):
         if dice_expression[1] == 'f':
            result = roll_fudge_die()
         else:
            result = roll(int(dice_expression[1]))
         val[0] += result
         val[1] = val[1] + f', {result}'
      val[1] = f"({val[1][2:]})"
      return val
   except:
      return None

def resolve_advantage():
   a = roll(20)
   b = roll(20)
   val = [0, ""]
   val[0] = max(a, b)
   val[1] = f'max({a}, {b})'
   return val

def resolve_disadvantage():
   a = roll(20)
   b = roll(20)
   val = [0, ""]
   val[0] = min(a, b)
   val[1] = f'min({a}, {b})'
   return val

def roll(val):
   return random.randint(1, val)

def roll_fudge_die():
   return random.randint(-1, 1)

def generate_interlude():
   return random.choice(interludes)

def resolve_all_operators(val_list, operator_list):
   try:
      sum = val_list[0][0];
      val_index = 1
      while val_index < len(val_list):
         sum = resolve_single_operator(sum, val_list[val_index][0], operator_list[val_index - 1])
         val_index += 1
      return sum
   except:
      return None

def resolve_single_operator(sum, val, op):
   if op == "+":
      return sum + val
   elif op == "-":
      return sum - val
   elif op == "/":
      return sum / val
   elif op == "x" or op == "*":
      return sum * val
   return None

def roll_stat_block():
   stat = []
   rolled_str = []
   for i in range(8):
      roll_arr = roll_single_stat()
      sum = roll_arr[0] + roll_arr[1] + roll_arr[2] + roll_arr[3] - min(roll_arr)
      rolled_str.append(f'{sum} ({roll_arr[0]}, {roll_arr[1]}, {roll_arr[2]}, {roll_arr[3]})')
      stat.append(sum)
   stat.sort(reverse=True)
   stat = stat[0:-2]
   out_str = "**Results : "
   for i in range(0, 6):
      out_str += f'{stat[i]}'
      if i < 5:
         out_str += ", "
      else:
         out_str += "**"
   for element in rolled_str:
      out_str += "\n  " + element
   return out_str

def roll_single_stat():
   return [roll(6), roll(6), roll(6), roll(6)]

def generate_kung_fu(reps):
   reps = max(1, reps)
   reps = min(20, reps)
   out_str = ""
   for i in range(reps):
      out_str = "{}\n{}".format(out_str, kung_fu_generator.roll())
   return out_str

def generate_names(cmd, int_arg):
   str_list = cmd.split()
   str_list.append("")   # beacuse not everything needs a gender
   reps = 5
   if int_arg != 0:
      reps = int_arg
   reps = max(1, reps)
   reps = min(20, reps)
   out_str = ""
   try:
      for i in range(0, reps):
         out_str += get_single_name(str_list[1], str_list[2]) + "\n"
      out_str = out_str[:-1] # trim the last newline
      return out_str
   except:
      return message_dict["nameParsingFailure"].format(cmd)

def get_single_name(race, sex):
   if race == "dragonborn":
      if sex == "female":
         return "{} {}".format(name_dict["dragonborn_female"].generate(), name_dict["dragonborn_surname"].generate())
      elif sex == "male":
         return "{} {}".format(name_dict["dragonborn_male"].generate(), name_dict["dragonborn_surname"].generate())
   elif race == "dwarf":
      if sex == "female":
         return "{} {}".format(name_dict["dwarf_female"].generate(), name_dict["dwarf_surname"].generate())
      elif sex == "male":
         return "{} {}".format(name_dict["dwarf_male"].generate(), name_dict["dwarf_surname"].generate())
   elif race == "elf":
      if sex == "female":
         return "{} {}".format(name_dict["elf_female"].generate(), name_dict["elf_surname"].generate())
      elif sex == "male":
         return "{} {}".format(name_dict["elf_male"].generate(), name_dict["elf_surname"].generate())
   elif race == "european":
      if sex == "female":
         return "{} {}".format(name_dict["european_female"].generate(), name_dict["european_surname"].generate())
      elif sex == "male":
         return "{} {}".format(name_dict["european_male"].generate(), name_dict["european_surname"].generate())
   elif race == "gnome":
      if sex == "female":
         return "{} {}".format(name_dict["gnome_female"].generate(), name_dict["gnome_surname"].generate())
      elif sex == "male":
         return "{} {}".format(name_dict["gnome_male"].generate(), name_dict["gnome_surname"].generate())
   elif race == "halfling":
      if sex == "female":
         return "{} {}".format(name_dict["halfling_female"].generate(), name_dict["halfling_surname"].generate())
      elif sex == "male":
         return "{} {}".format(name_dict["halfling_male"].generate(), name_dict["halfling_surname"].generate())
   elif race == "orc":
      if sex == "female":
         return name_dict["orc_female"].generate()
      elif sex == "male":
         return name_dict["orc_male"].generate()
   elif race == "angel":
      return name_dict["angel"].generate()
   elif race == "demon":
      return name_dict["demon"].generate()
   elif race == "dragon":
      return name_dict["dragon"].generate()
   print("bad name request {} {}".format(race, sex))
   raise Exception("bad name request {} {}".format(race, sex))
   return None

# stuff for relic generation
def get_creator():
   return random.choice(relic_creator)

def get_history():
   return random.choice(relic_history)

def get_quirk():
   return random.choice(relic_quick)

def get_relic_minor_prop():
   out_str1 = random.choice(relic_minor_prop)
   out_str2 = ""
   if out_str1 == "ROLL_TWICE":
      out_str2 = random.choice(relic_minor_prop)
   while out_str1 == "ROLL_TWICE":
      out_str1 = random.choice(relic_minor_prop)
   while out_str2 == out_str1 or out_str2 == "ROLL_TWICE":
      out_str2 = random.choice(relic_minor_prop)
   if out_str2 != "":
      out_str1 += "\n"
   return out_str1 + out_str2

def generate_relic():
   return relic_dict["format"].format(get_creator(), get_history(), get_relic_minor_prop(), get_quirk())

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