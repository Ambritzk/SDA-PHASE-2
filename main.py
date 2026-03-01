import json
import sys
from core.engine import Orchestrator
from plugins.input import CSVReader, JSONReader
from plugins.output import ConsoleWriter, GraphicsChartWriter



outputChoices = {
    "1": ConsoleWriter,
    "2": GraphicsChartWriter
}
InputChoices = {
    "1": CSVReader,
    "2": JSONReader
}

validKeys = {
    "Reader",
    "Writer",
    "Continent",
    "TargetYear",
    "StartYear",
    "EndYear",
    "OutputTimeline"
}
validContinents = {
    "Asia",
    "Europe",
    "Africa",
    "North America",
    "South America",
    "Oceania"
}

def ReadConfig() -> dict:
    try:
        with open("config.json","r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Something seems to be wrong with the config.json file")
    return {}

def CheckKeys(config: dict) -> bool:
    tolower = lambda x: {k.lower() for k in x}
    for key in validKeys:
        if key.lower() not in tolower(config.keys()):
            print(key, "is missing in config.json")
            return False

def CheckContinent(config: dict) -> bool:
    if type(config.get("Continent")) is not str:
        return False
    if config.get("Continent").title() not in validContinents:
        return False
    return True
def CheckTargetYear(config: dict) -> bool:
    if type(config.get("TargetYear")) is not int:
        print("Target Year must be an integer")
        return False
    year: int = int(config.get("TargetYear"))
    if not 1960 <= year <= 2022:
        print("Target year must be between 1960 and 2022. Fix config.json")
        return False
    return True
def CheckYearRange(config: dict) -> bool:
    if type(config.get("StartYear")) is not int:
        print("Start Year must be an integer")
        return False
    if type(config.get("EndYear")) is not int:
        print("End Year must be an integer")
        return False
    
    startyear: int = int(config.get("TargetYear"))
    endyear: int = int(config.get("EndYear"))

    if 1960 <= startyear <= 2022:
        if endyear >= startyear:
            if endyear > 2022:
                print("End year must be between 1960 and 2022. Fix config.json")
                return False
            return True
        else:
            print("Start year must be less than or equal to the end year.",end = "")
    else:
        print("Start year must be between 1960 and 2022. Fix config.json")
    print("Fix config.json and try again")
    return False



def CheckTimeLine(config: dict) -> bool:
    if type(config.get("OutputTimeline")) is not str:
        print("OutputTimeline must be string. Fix config.json")
        return False
    if config.get("OutputTimeline").lower() not in ["range","specificyear"]:
        print('OutputTimeline can only be "range" or "SpecificYear". Fix config.json')
        return False
    return True
def CheckWriter(config: dict) -> bool:
    if type(config.get("Writer")) is not str:
        print("Writer must be string. Fix config.json")
        return False
    if config.get("Writer").lower() not in ["consolewriter","graphicschartwriter"]:
        print('Writer can only be "ConsoleWriter" or "GraphicsChartWriter".Fix config.json')
        return False
    return True
def CheckReader(config: dict) -> bool:
    if type(config.get("Reader")) is not str:
        print("Reader must be string. Fix config.json")
        return False
    if config.get("Reader").lower() not in ["csvreader","jsonreader"]:
        print('Reader can only be "CSVReader" or "JSONReader".Fix config.json')
        return False
    return True

def ConfigChecks(config:dict) -> bool:
    continent: bool = CheckContinent(config)
    target: bool = CheckTargetYear(config)
    ranges: bool = CheckYearRange(config)
    timeline: bool = CheckTimeLine(config)
    writer: bool = CheckWriter(config)
    reader: bool = CheckReader(config)
    return continent and target and ranges and timeline and writer and reader

def getWriterID(config:dict) -> str:
    if config.get("Writer").lower() == 'consolewriter':
        return '1'

    else:
        return '2'
def getReaderID(config:dict) -> str:
    if config.get("Reader").lower() == 'csvreader':
        return '1'

    else:
        return '2'



def MAIN() -> None:
    print("Welcome to the Orchestra, Have a look around")
    print(".__ . ._.. _._. ___ __ . ")
    print("  Data References:")
    print("  Available Continents are: Asia, Europe, Africa, North America, South America, Oceania")
    print("  Available Years are: 1960 - 2022")
    print("... . ._.. . _._. _")
    print()


    config : dict = ReadConfig()
    if config == {}:
        sys.exit(3)

    if ConfigChecks(config) == False:
        sys.exit(2)

    writerClass = outputChoices.get(getWriterID(config))
    ReaderClass = InputChoices.get(getReaderID(config))
    print(getReaderID(config))
    sink = writerClass()

    try:
        engine = Orchestrator(sink=sink, configFile=config)
        source = ReaderClass(engine)
        source.run()
    except Exception as e:
        print()
        print("Something has broken, lol, json it's you again?")
        sys.exit(1)


if __name__ == "__main__":
    MAIN()