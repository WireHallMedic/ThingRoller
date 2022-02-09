# simple text cleaning tool

import re

fileName = "name_dragon.txt"

text = open(fileName, "r").read()
text = re.sub("\([^\)]*\)", "", text)
text = re.sub("\[[^\]]*\]", "", text)

file = open(fileName, 'w')
file.write(text)
file.close()