import csv
import json
#import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
from core.contracts import PipelineService

class CSVReader:
    def __init__(self, service: PipelineService) -> None:
        self.service = service
        file_path = Path(__file__).parent.parent.absolute() / 'data' / 'gdp_with_continent_filled.xlsx - GDP.csv'
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.data = list(reader)

    def run(self) -> None:
        self.service.execute(self.data)


class JSONReader:
    service: PipelineService
    data: List[dict] 
    def __init__(self, ServiceFromCore: PipelineService) -> None:
        self.service = ServiceFromCore
        #First we need to get the csv file. We therefore go to the parent directory and then enter into the data directory
        file_path = Path(__file__).parent.parent.absolute() / 'data' / 'gdp_with_continent_filled.json'
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                raw_data = file.read()
                valid = raw_data.replace('#@$!\\','NaN').replace('NaN','0')
                final = json.loads(valid)
                self.data = final
        except FileNotFoundError:
            print('"gdp_with_continent_filled.json" not found')

            
    def run(self):
        self.service.execute(self.data)


# def mm():
#     file_path = Path(__file__).parent.parent.absolute() / 'data' / 'gdp_with_continent_filled.json'
#     with open(file_path, "r", encoding="utf-8") as file:
#         raw_data = file.read()
#         valid = raw_data.replace('#@$!\\','NaN')
#         f = valid.replace('NaN','0')
#         final = json.loads(f)
#         print(pd.DataFrame(final))
# mm()