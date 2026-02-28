import csv
from typing import List, Dict, Any
from pathlib import Path
class CSVREADER:
    data: List[Dict]
    def __init__(self, FileName: str) -> None:
        with open(FileName,"r") as file:
            Reader = csv.DictReader(file)
            self.data = [row for row in Reader]


    def __str__(self):
        return f"{self.data}"

def main():
    filepath = Path(__file__).cwd().parent / 'data/gdp_with_continent_filled.xlsx - GDP.csv'
    print(filepath)
    pp = CSVREADER(filepath)
    print(pp);

main()
