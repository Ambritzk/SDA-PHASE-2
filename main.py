import json
import sys
from core.engine import Orchestrator
from plugins.input import CsvReader
from plugins.output import ConsoleWriter, GraphicsChartWriter

outputChoices = {
    "1": ConsoleWriter,
    "2": GraphicsChartWriter
}

validContinents = {
    "Asia",
    "Europe",
    "Africa",
    "North America",
    "South America",
    "Oceania"
}


def choiceContinent() -> str:
    continent = input("Enter a Continent (e.g. Asia): ").strip().title()
    if continent in validContinents:
        return continent
    print("Invalid entry. Please enter a valid continent exactly as listed above.")
    print()
    return choiceContinent()


def choiceTargetYear() -> int:
    targetYearStr = input("Enter Target Year (1960-2022) OR enter 0 to specify a date range: ").strip()
    if targetYearStr == "0":
        return 0
    if targetYearStr.isdigit() and 1960 <= int(targetYearStr) <= 2022:
        return int(targetYearStr)
    print("Invalid year. Please enter a numeric year between 1960 and 2022, or 0 for a range.")
    print()
    return choiceTargetYear()


def choiceStartYear() -> int:
    startYearStr = input("Enter Start Year for Range (e.g., 2010): ").strip()
    if startYearStr.isdigit() and 1960 <= int(startYearStr) <= 2022:
        return int(startYearStr)
    print("Invalid start year. Please enter a numeric year between 1960 and 2022.")
    print()
    return choiceStartYear()


def choiceEndYear(startYear: int) -> int:
    endYearStr = input("Enter End Year for Range (e.g., 2020): ").strip()
    if endYearStr.isdigit() and 1960 <= int(endYearStr) <= 2022:
        endYear = int(endYearStr)
        if endYear >= startYear:
            if endYear == startYear:
                print(
                    f"Start and End Year are both {startYear}. Pipeline will process data strictly for this single year.")
                print()
            return endYear
        print(f"Invalid range. End Year ({endYear}) must be greater than or equal to Start Year ({startYear}).")
        print()
    else:
        print("Invalid end year. Please enter a numeric year between 1960 and 2022.")
        print()
    return choiceEndYear(startYear)


def choiceOutput() -> str:
    choice = input("Choice (1 or 2): ").strip()
    if choice in outputChoices:
        return choice
    print("Invalid choice. Please enter 1 or 2.")
    print()
    return choiceOutput()


def configWork() -> dict:
    continent = choiceContinent()
    targetYear = choiceTargetYear()

    if targetYear == 0:
        startYear = choiceStartYear()
        endYear = choiceEndYear(startYear)
        return {
            "Continent": continent,
            "TargetYear": endYear,
            "StartYear": startYear,
            "EndYear": endYear,
            "DeclineYears": 5
        }

    return {
        "Continent": continent,
        "TargetYear": targetYear,
        "StartYear": targetYear,
        "EndYear": targetYear,
        "DeclineYears": 5
    }


def writeConfig(configData: dict) -> None:
    with open("config.json", "w") as f:
        json.dump(configData, f, indent=4)


def MAIN() -> None:
    print("Welcome to the Orchestra, Have a look around")
    print(".__ . ._.. _._. ___ __ . ")
    print("  Data References:")
    print("  Available Continents are: Asia, Europe, Africa, North America, South America, Oceania")
    print("  Available Years are: 1960 - 2022")
    print("... . ._.. . _._. _")
    print()

    configData = configWork()

    print()
    print("Select Output Sink Choioce:")
    print("1. Console Output (Text/Data)")
    print("2. Graphics Chart Output (Matplotlib UI)")
    choice = choiceOutput()

    writeConfig(configData)

    writerClass = outputChoices.get(choice, ConsoleWriter)
    sink = writerClass()

    try:
        engine = Orchestrator(sink=sink, configPath="config.json")
        source = CsvReader(service=engine)
        source.run()
    except Exception as e:
        print()
        print("Something has broken, lol, json it's you again?")
        sys.exit(1)


if __name__ == "__main__":
    MAIN()