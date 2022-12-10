import discord
import discord.ext
from discord.ext.commands import Bot
import json
import re
import os
import io
import random
import name_gen
import deck
import dice
import socket
import subtable_main
import fate_roller
import PIL

#constants
INT_REG_EX = "\d+"
SHOULD_CALCULATE_REG_EX = "^[+\-\d]|^d\d|^advantage|^disadvantage|\d+df"

NOT_YET_IMPLEMENTED_STR = ":warning: This feature is not yet implemented :warning:"
ADMIN_NAME = "wire_hall_medic"

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

#fate dice object
fate_dice = fate_roller.FateRoller()

# table-based generators
kung_fu_generator = subtable_main.TableController("text_files/kung_fu.txt")
quest_generator = subtable_main.TableController("text_files/quest_parts.txt")
tavern_generator = subtable_main.TableController("text_files/taverns.txt")

intents = discord.Intents.default()
intents.messages = True
# client = discord.Client(intents=intents)
client = Bot(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')
    
# voice channels
@client.command(name='join',aliases = ['summon']) # CREATING COMMAND "JOIN" WITH ALIAS SUMMON
async def _join(ctx, *, channel: discord.VoiceChannel = None): # TAKING ARGUMENT CHANNEL SO PPL CAN MAKE THE BOT JOIN A VOICE CHANNEL THAT THEY ARE NOT IN
   """Joins a voice channel."""
   destination = channel if channel else ctx.author.voice.channel # CHOOSING THE DESTINATION, MIGHT BE THE REQUESTED ONE, BUT IF NOT THEN WE PICK AUTHORS VOICE CHANNEL

   if ctx.voice_client: # CHECKING IF THE BOT IS PLAYING SOMETHING
      await ctx.voice_state.voice.move_to(destination) # IF THE BOT IS PLAYING WE JUST MOVE THE BOT TO THE DESTINATION
      return

   await destination.connect() # CONNECTING TO DESTINATION
   await ctx.send(f"Succesfully joined the voice channel: {destination.name} ({destination.id}).")
    
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
   out_file = None
   
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
      out_str = dice.roll_stat_block()
      
   # roll tavern
   if re.search("^tavern", cmd):
      out_str = generate_tavern(int_arg)
   
   if re.search("^kung fu", cmd):
      out_str = generate_kung_fu(int_arg)
      
   # roll interlude
   if cmd == "interlude":
      out_str = generate_interlude()
      
   # aliases for Fate dice (4dF are special, other xdF handled by dice roller)
   if cmd == "fudge" or cmd == "4df" or cmd == "fate":
      cmd = "fate"
      roll_obj = fate_dice.roll()
      out_str = roll_obj[0].replace("[", "(").replace("]", ")")
      out_str = "**" + out_str.split(" ", 1)[0] + "** " + out_str.split(" ", 1)[1]
      # save image because we need a file
      roll_obj[1].save("last_roll.png", "PNG")
      with open("last_roll.png", 'rb') as f:
         out_file = discord.File(f)
      
   
   #roll some dice and/or calculate
   if re.search(SHOULD_CALCULATE_REG_EX, cmd) != None:
      out_str = dice.resolve_dice_expression(cmd.replace("*", "x"))
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
   
   # mixed output
   if out_file != None and out_str != None:
      await message.channel.send(out_str, file=out_file)
      return
   
   # return result
   if out_str != None:
      await message.channel.send(out_str)
      return

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

def generate_interlude():
   return random.choice(interludes)

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