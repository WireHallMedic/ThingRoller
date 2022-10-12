from PIL import Image
import random as rng

class FateRoller:
   def __init__(self):
      self.blank_img = Image.open(f"Blank Die.png")
      self.plus_img = Image.open(f"Plus Die.png")
      self.minus_img = Image.open(f"Minus Die.png")
      self.die_size = self.blank_img.width
   
   def _get_image(self, val):
      if val == -1:
         return self.minus_img
      elif val == 1:
         return self.plus_img
      return self.blank_img
   
   def _roll_dice(self):
      roll_array = []
      for i in range(4):
         roll_array.append(rng.sample([-1, 0, 1], 1)[0])
      return roll_array
   
   def _get_sum_str(self, arr):
      sum = 0
      for val in arr:
         sum += val
      prefix = ""
      if sum > -1:
         prefix = "+"
      return f"{prefix}{sum} {arr}"
   
   def _create_image(self, arr):
      img = Image.new("RGBA", (self.die_size * 4, self.die_size))
      for i in range(4):
         inset = i * self.die_size
         die_img = self._get_image(arr[i])
         img.paste(die_img, (inset, 0))
      return img
   
   def roll(self):
      arr = self._roll_dice()
      sum = self._get_sum_str(arr)
      img = self._create_image(arr)
      return (sum, img)
   
if __name__ == "__main__":
   roll = FateRoller().roll()
   print(roll[0])
   roll[1].show()