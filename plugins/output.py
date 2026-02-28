from typing import List, Dict
import pandas as pd


class ConsoleWriter:
    def write(self, records: List[dict]) -> None:
        self.printAll(records)
    def printAll(self,records: List[dict]) -> None:
        print(pd.DataFrame(records))

#Create class for creating graphs here