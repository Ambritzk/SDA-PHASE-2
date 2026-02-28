from typing import List, Dict, Any
from contracts import DataSink

class TransformationEngine:
    config_info: Dict
    def __init__(self, config:Dict, sink: DataSink):
        # The specific writer is 'injected' at runtime
        self.sink = sink 
        self.config_info = config

    def FixNullCells(list_of_dicts: List[Dict]) -> List[Dict]:
        get_value = lambda v: 0 if v == '' else v
        get_wrongCell = lambda v: "Wrong cell" if v == '' else v
        clean_row = lambda d: {k: get_value(v) if k.isdecimal() else get_wrongCell(v) for k, v in d.items()}
        
        
        fixedList = list(map(clean_row, list_of_dicts))

        for dictionary in fixedList:
            if "Wrong cell" in dictionary.values():
                return "One of the columns is missing a value."
            

        return fixedList




    def execute(self, raw_data: List[Any]) -> None:
        # 1. Transform data
        # 2. Send to the abstraction

        #Filter data here according to config.json
        fixed_data = self.FixNullCells(raw_data)
        subset = list(filter(lambda row: row.get('Continent') == self.config_info["Continent"], fixed_data))
        self.sink.write(subset)


