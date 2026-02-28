from typing import List, Dict, Any
from plugins.input import CSVREADER
from plugins.output import ConsoleWriter
from core.contracts import DataSink, PipelineService
from core.engine import TransformationEngine
import json


INPUT_DRIVERS = {"csv": CSVREADER}
OUTPUT_DRIVERS = {"console": ConsoleWriter}


def ReadConfig() -> Dict:
    with open("config.json","r") as file:
        return json.load(file)


config : Dict = ReadConfig()
print(config)

if(config["Input"].lower() == "csvreader"):
    ReaderClass: PipelineService = INPUT_DRIVERS["csv"]

if(config["Output"].lower() == "console"):
    Sink: DataSink = OUTPUT_DRIVERS["console"]
    Sinkobj = Sink()

    #Let that sink in
    #to the core
    core = TransformationEngine(config,Sinkobj)
    Reader = ReaderClass(core)

    Reader.run()