import csv
from typing import List, Dict, Any
from pathlib import Path
import json
import re
from core.contracts import PipelineService
class CSVREADER:
    service: PipelineService
    data: List[Dict] 
    def __init__(self, ServiceFromCore: PipelineService) -> None:
        service = ServiceFromCore
        #First we need to get the csv file. We therefore go to the parent directory and then enter into the data directory
        filePath = Path(__file__).cwd().parent / 'data/gdp_with_continent_filled.xlsx - GDP.csv'
        with open(filePath,"r") as file:
            Reader = csv.DictReader(file)
            self.data = [row for row in Reader]
    def run(self):
        self.service.execute(self.data)

