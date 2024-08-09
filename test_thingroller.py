# testing for thingroller.
import pytest
import dice

if __name__ == "__main__":
   assert dice.resolve_dice_expression("3d6 + 5 - 1d4 / 5 * 4") is not None
   assert dice.resolve_dice_expression("3d6 + 5 j 1d4 / 5 * 4", True) is None
   assert dice.resolve_advantage() is not None
   assert dice.resolve_disadvantage() is not None
   assert dice.roll(6) is not None
   exploded_die = False
   for i in range(100):
      if dice.roll(2, True) > 2:
         exploded_die = True
         break
   assert exploded_die
   assert dice.roll_fudge_die() is not None
   assert dice.roll_stat_block() is not None
   
