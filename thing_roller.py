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
#client = discord.Client(intents=intents)
client = Bot(command_prefix = "!", intents = intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')

# table of contents
@client.command()
async def thingroller(ctx, *args):
   out_str = message_dict["botInfo"]
   for key in message_dict["recognizedCommands"]:
      out_str += "\n  " + key + " " + message_dict["recognizedCommands"][key]
   out_str += "\n" + message_dict["commandNotes"]
   await ctx.send(out_str)
   
# status
@client.command()
async def status(ctx, *args):
   out_str = message_dict["goodStatus"]
   addr = getIPAddress()
   out_str = "{}\nHostname: {}\nIP Address: {}".format(out_str, addr[0], addr[1]);
   await ctx.send(out_str)

# examples
@client.command()
async def examples(ctx, *args):
   out_str = "__Examples of Things I Can Calculate__:\n"
   out_str += message_dict["formatExamples"] + "\n"
   out_str += message_dict["formatNotes"]
   await ctx.send(out_str)
   
# stat block
@client.command()
async def statblock(ctx, *args):
   await ctx.send(dice.roll_stat_block())

# fudge
@client.command()
async def fudge(ctx, *args):
   await do_fudge_roll(ctx, args)

# fate
@client.command()
async def fate(ctx, *args):
   await do_fudge_roll(ctx, args)

# work method for fudge/fate
async def do_fudge_roll(ctx, args):
   roll_obj = fate_dice.roll()
   out_str = roll_obj[0].replace("[", "(").replace("]", ")")
   out_str = "**" + out_str.split(" ", 1)[0] + "** " + out_str.split(" ", 1)[1]
   # save image because we need a file
   roll_obj[1].save("last_roll.png", "PNG")
   with open("last_roll.png", 'rb') as f:
      out_file = discord.File(f)
   await ctx.send(content=out_str, file=out_file)

# tavern
@client.command()
async def tavern(ctx, *args):
   try:
      int_arg = get_int_arg(args)
      await ctx.send(generate_tavern(int_arg))
   except:
      await ctx.send(f"Unable to understand '{args[0]}'.")

# interlude
@client.command()
async def interlude(ctx, *args):
   await ctx.send(generate_interlude())

# relic
@client.command()
async def relic(ctx, *args):
   await ctx.send(generate_relic())

# quest
@client.command()
async def quest(ctx, *args):
   try:
      int_arg = get_int_arg(args)
      num_of_quests = max(1, int_arg)
      num_of_quests = min(5, num_of_quests)
      out_str = ""
      for i in range(num_of_quests):
         out_str = out_str + quest_generator.roll() + "\n"
      out_str = out_str.strip()
      await ctx.send(generate_tavern(int_arg))
   except:
      await ctx.send(f"Unable to understand '{args[0]}'.")

# kungfu
@client.command()
async def kungfu(ctx, *args):
   try:
      int_arg = get_int_arg(args)
      await ctx.send(generate_kung_fu(int_arg))
   except:
      await ctx.send(f"Unable to understand '{args[0]}'.")

# shuffle
@client.command()
async def shuffle(ctx, *args):
   deck.shuffle()
   out_str = "Deck reshuffled"
   await ctx.send(out_str)

# jokers
@client.command()
async def jokers(ctx, *args):
   deck.shuffle(True)
   out_str = "Deck reshuffled (jokers included)."
   await ctx.send(out_str)

# nojokers
@client.command()
async def nojokers(ctx, *args):
   deck.shuffle(True)
   out_str = "Deck reshuffled (jokers excluded)."
   await ctx.send(out_str)

# draw
@client.command()
async def draw(ctx, *args):
   int_arg = get_int_arg(args)
   num_to_draw = max(1, int_arg)
   num_to_draw = min(52, num_to_draw)
   out_str = ""
   for i in range(num_to_draw):
      out_str = out_str + str(deck.draw_card()) + " "
   await ctx.send(out_str)

# roll
@client.command()
async def roll(ctx, *, arg_str):
   await do_roll(ctx, arg_str)

# r
@client.command()
async def r(ctx, *, arg_str):
   await do_roll(ctx, arg_str)

# name
@client.command()
async def name(ctx, *, arg_str):
   try:
      name_args = get_args_for_name(arg_str)
      name_list = generate_names(name_args[0], name_args[1])
      await ctx.send(name_list)
   except:
      await ctx.send(f"Unable to understand '{args[0]}'.")

# roll some dice and/or calculate
async def do_roll(ctx, arg_str):
   if re.search(SHOULD_CALCULATE_REG_EX, arg_str) != None:
      out_str = dice.resolve_dice_expression(arg_str.replace("*", "x"))
   if out_str == None:
      out_str = message_dict["parsingFailure"].format(arg_str)
   await ctx.send(out_str)
   
# extracts last argument if longer than min length, else 1
def get_int_arg(args, min_length = 0):
   int_arg = 1
   try:
      split_args = arg_str.split(" ")
      if len(split_args) > min_length:
         last_arg = split_args.pop()
         int_arg = int(last_arg)
      return int_arg
   except:
      return 1

# return a tuple of the main argument string, and the int arg
def get_args_for_name(arg_str):
   int_arg = 1
   try:
      split_args = arg_str.split(" ")
      last_arg = split_args.pop()
      int_arg = int(last_arg)
      arg_str = arg_str.replace(last_arg, "").strip()
      return (arg_str, int_arg)
   except:
      return (arg_str, 1)

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
         out_str += get_single_name(str_list[0], str_list[1]) + "\n"
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