import re
import random

INT_REG_EX = "\d+"
OPERATOR_REG_EX = "[+\-/*x]"

MAX_DICE = 1000000

def resolve_dice_expression(dice_expression, suppress_exception_message = False):
   try:
      # strip out spaces
      dice_expression = dice_expression.replace(" ", "")
      # check for explosions
      exploding = False
      if dice_expression.startswith("e"):
         exploding = True
         dice_expression = dice_expression[1:]
      if dice_expression.startswith("-e"):
         exploding = True
         dice_expression = dice_expression[2:]
      # if it starts with a negative number or expression, put in a zero
      if dice_expression[0] == "-":
         dice_expression = "0" + dice_expression
      # make lists of expressions and operators
      expression_list = re.split(OPERATOR_REG_EX, dice_expression)
      operator_list = re.findall(OPERATOR_REG_EX, dice_expression)
      # resolve expressions
      val_list = []
      for val in expression_list:
         val_list.append(resolve_single_dice_expression(val, exploding, suppress_exception_message))
      # resolve operators
      sum = resolve_all_operators(val_list, operator_list);
      # compile output
      out_str = f'**Result: {sum}**\n'
      out_str += "Rolled: "
      out_str += val_list[0][1]
      for i in range(1, len(val_list)):
         out_str += " " + operator_list[i - 1] + " " + val_list[i][1]
      return out_str
   except Exception as ex:
      if not suppress_exception_message:
         print(ex)
      return None

def resolve_single_dice_expression(dice_expression, exploding, suppress_exception_message):
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
      if dice_expression[0] == "":
         dice_expression[0] = "1"
      iterations = int(dice_expression[0])
      result = 0
      if iterations > MAX_DICE:
         return None
      for i in range(iterations):
         if dice_expression[1] == 'f':
            result = roll_fudge_die()
         else:
            result = roll(int(dice_expression[1]), exploding)
         val[0] += result
         val[1] = val[1] + f', {result}'
      val[1] = f"({val[1][2:]})"
      return val
   except Exception as ex:
      if not suppress_exception_message:
         print(ex)
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

def roll(val, exploding = False):
   rolled_val = random.randint(1, val)
   total = rolled_val
   while rolled_val == val and exploding == True:
      rolled_val = random.randint(1, val)
      total += rolled_val
   return total

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
   for i in range(6):
      roll_arr = roll_single_stat()
      sum = roll_arr[0] + roll_arr[1] + roll_arr[2] + roll_arr[3] - min(roll_arr)
      rolled_str.append(f'{sum} ({roll_arr[0]}, {roll_arr[1]}, {roll_arr[2]}, {roll_arr[3]})')
      stat.append(sum)
   stat.sort(reverse=True)
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

