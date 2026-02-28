from typing import List, Dict, Any
from plugins.input import CSVREADER
import json
def ReadConfig() -> Dict:
    with open("config.json","r") as file:
        return json.load(file)


config : Dict = ReadConfig()
print(config)

