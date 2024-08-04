# testing for thingroller.

import dice

if __name__ == "__main__":
   dice.resolve_dice_expression("3d6 + 5 - 1d4 / 5 * 4")
   dice.resolve_advantage()
   dice.resolve_disadvantage()
   dice.roll(6)
   for i in range(1000):
      if dice.roll(6, True) > 6:
         break
      if i == 99:
         raise Exception("No exploding 6 in a thousand tries") 
   dice.roll_fudge_die()
   dice.roll_stat_block()
   
