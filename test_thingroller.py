# testing for thingroller.
import pytest
import dice
import random

def test_basics():
   random.seed(10000)
   assert dice.resolve_dice_expression("3d6 + 5 - 1d4 / 5 * 4") == "**Result: 10.4**\nRolled: (5, 3, 1) + 5 - (1) / 5 * 4"
   assert dice.resolve_dice_expression("3d6 + 5 j 1d4 / 5 * 4", suppress_exception_message = True) is None
   assert dice.resolve_advantage() == [9, 'max(1, 9)']
   assert dice.resolve_disadvantage() == [11, 'min(17, 11)']
   assert dice.roll(6) == 2
   assert dice.roll_fudge_die() is not None
   assert dice.roll_stat_block() is not None
   assert dice.resolve_dice_expression("3d6, 1d6 + 5") == "**Result: 6, 9**\nRolled: (2, 1, 3), 2"

def test_explosions():
   random.seed(10000)
   assert dice.roll(2, exploding = True) == 3
   random.seed(10000)
   assert dice.roll(2, exploding = False) == 2
   random.seed(10000)
   assert dice.resolve_dice_expression("e 1d2") == "**Result: 3**\nRolled: (3)"
   random.seed(10000)
   assert dice.resolve_dice_expression("-e 1d2") == "**Result: 3**\nRolled: (3)"
   random.seed(10000)
   assert dice.resolve_dice_expression("1d2") == "**Result: 2**\nRolled: (2)"
   assert dice.resolve_dice_expression(" e 3d6, 1d6 + 5") == "**Result: 15, 18**\nRolled: (1, 7, 7), 1"
   

if __name__ == "__main__":
   test_basics()
   test_explosions()
