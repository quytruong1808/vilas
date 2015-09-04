from os import listdir
import os
import os.path

#Delete water and ions
clear_words = [' HOH ', ' CL ', ' NA ']

for file in listdir('input/receptor'):
  print file
  with open('input/receptor/'+file) as oldfile, open('input/receptor/new_'+file, 'w') as newfile:
    for line in oldfile:
      if not any(clear_word in line for clear_word in clear_words):
          newfile.write(line)
    os.remove('input/receptor/'+file)
    os.rename('input/receptor/new_'+file, 'input/receptor/'+file)

for file in listdir('input/ligand'):
  with open('input/ligand/'+file) as oldfile, open('input/ligand/new_'+file, 'w') as newfile:
    for line in oldfile:
      if not any(clear_word in line for clear_word in clear_words):
        newfile.write(line)
