from typing import List, Dict

from core.contracts import DataSink
class ConsoleWriter:
    def write(self,records: List[Dict]):
        self.Top10(records)

    def Top10(self,records: List[Dict]):
        #an example for countries with the top 10 gdp for a year
        sorted_list = sorted(self.records, key = lambda x: float(self.records["gdp"]))
        print(sorted_list)