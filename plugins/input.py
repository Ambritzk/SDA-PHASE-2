import csv
from typing import List, Dict, Any
from pathlib import Path
from core.contracts import PipelineService

class CsvReader:
    def __init__(self, service: PipelineService) -> None:
        self.service = service
        file_path = Path(__file__).parent.parent.absolute() / 'data' / 'gdp_with_continent_filled.xlsx - GDP.csv'
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.data = list(reader)

    def run(self) -> None:
        self.service.execute(self.data)