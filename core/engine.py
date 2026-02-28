from typing import List, Dict, Any
from core.contracts import DataSink
import pandas as pd
class TransformationEngine:
    config: Dict
    def __init__(self, configFromMain:Dict, sink: DataSink):
        # The specific writer is 'injected' at runtime
        self.sink = sink 
        self.config = configFromMain

    def FixNullCells(self,list_of_dicts: List[Dict]) -> List[Dict]:
        get_value = lambda v: 0 if v == '' else v
        get_wrongCell = lambda v: "Wrong cell" if v == '' else v
        clean_row = lambda d: {k: get_value(v) if k.isdecimal() else get_wrongCell(v) for k, v in d.items()}
        
        
        fixedList = list(map(clean_row, list_of_dicts))

        for dictionary in fixedList:
            if "Wrong cell" in dictionary.values():
                return "One of the columns is missing a value."
            

        return fixedList




    def execute(self, raw_data: List[dict]) -> None:
        # 1. Transform data
        # 2. Send to the abstraction

        #Filter data here according to config.json
        fixed_data = self.FixNullCells(raw_data)
        records: List[dict] = list(filter(lambda row: row.get('Continent').lower() == self.config["Continent"].lower(), fixed_data))
        self.sink.write(records)


