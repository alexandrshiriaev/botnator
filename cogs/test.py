import os
import json 
def jsonload(path):
    if os.path.isfile(path):
        with open(path, 'r') as f:
            if f.read() != '':
                array = json.load(f)
            else:
                array = []
    else:
        with open(path, 'w') as f:
            array = []
    return array
array = jsonload('cogs\coinsbot.json')