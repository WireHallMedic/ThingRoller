# testing for thingroller.
import pytest
import dice
import random

if __name__ == "__main__":
   random.seed(10000)
   assert dice.resolve_dice_expression("3d6 + 5 - 1d4 / 5 * 4") == "**Result: 10.4**\nRolled: (5, 3, 1) + 5 - (1) / 5 * 4"
   assert dice.resolve_dice_expression("3d6 + 5 j 1d4 / 5 * 4", suppress_exception_message = True) is None
   assert dice.resolve_advantage() == [9, 'max(1, 9)']
   assert dice.resolve_disadvantage() == [11, 'min(17, 11)']
   assert dice.roll(6) == 2
   exploded_die = False
   for i in range(100):
      if dice.roll(2, True) > 2:
         exploded_die = True
         break
   assert exploded_die
   assert dice.roll_fudge_die() is not None
   assert dice.roll_stat_block() is not None
