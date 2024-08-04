# testing for thingroller.

import dice

if __name__ == "__main__":
   print("resolve_dice_expression 3d6 + 5 - 1d4: {}".format(dice.resolve_dice_expression("3d6 + 5 - 1d4")))
   print("resolve_advantage: {}".format(dice.resolve_advantage()))
   print("resolve_disadvantage: {}".format(dice.resolve_disadvantage()))
   print("roll '1d6': {}".format(dice.roll(6)))
   print("roll 'e 1d6': {}".format(dice.roll(6, True)))
   print("roll_fudge_die: {}".format(dice.roll_fudge_die()))
   print("roll_stat_block: {}".format(dice.roll_stat_block()))
   
