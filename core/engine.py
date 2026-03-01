import json
import pycountry
from typing import List, Dict, Any
from core.contracts import DataSink


def loadConfig(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        raise ValueError(f"Configuration file '{path}' is missing or contains invalid JSON.")


def isCountry(row: dict) -> bool:
    return pycountry.countries.get(alpha_3=row.get('Country Code', '')) is not None


def getGdp(row: dict, year: str) -> float:
    try:
        val = row.get(str(year), 0)
        return float(val) if val else 0.0
    except (ValueError, TypeError):
        return 0.0


def filterCountries(data: List[Dict]) -> List[Dict]:
    return list(filter(isCountry, data))


def filterByContinent(data: List[Dict], continent: str) -> List[Dict]:
    def matchesContinent(countryRecord: dict) -> bool:
        return countryRecord.get('Continent') == continent

    return list(filter(matchesContinent, data))


def getTopBottomtebn(data: List[Dict], year: str, top: bool) -> List[Dict]:
    def hasValidGdp(countryRecord: dict) -> bool:
        return getGdp(countryRecord, year) > 0

    def extractGdp(countryRecord: dict) -> float:
        return getGdp(countryRecord, year)

    def formatResult(countryRecord: dict) -> Dict[str, Any]:
        return {"Country": countryRecord["Country Name"], "GDP": getGdp(countryRecord, year)}

    validData = list(filter(hasValidGdp, data))
    sortedData = sorted(validData, key=extractGdp, reverse=top)
    return list(map(formatResult, sortedData[:10]))


def calculateGrowth(startVal: float, endVal: float) -> float:
    return ((endVal - startVal) / startVal) * 100 if startVal else 0.0


def getGrowthRates(data: List[Dict], startYear: str, endYear: str) -> List[Dict]:
    def mapGrowthData(countryRecord: dict) -> Dict[str, Any]:
        growthValue = calculateGrowth(getGdp(countryRecord, startYear), getGdp(countryRecord, endYear))
        return {"Country": countryRecord["Country Name"], "Growth": growthValue}

    return list(map(mapGrowthData, data))


def getUniqueContinents(data: List[Dict]) -> set:
    def extractContinent(countryRecord: dict) -> str:
        return countryRecord.get('Continent')

    continents = set(map(extractContinent, data))
    continents.discard(None)
    continents.discard('')
    return continents


def calculateAvgGdpContinent(data: List[Dict], startYear: int, endYear: int) -> Dict[str, float]:
    continents = getUniqueContinents(data)
    years = [str(y) for y in range(startYear, endYear + 1)]

    def avgForContinent(cont: str) -> float:
        contData = filterByContinent(data, cont)
        if not contData: return 0.0

        def getGdpForYears(countryRecord: dict) -> float:
            return sum(map(lambda y: getGdp(countryRecord, y), years))

        totalGdp = sum(map(getGdpForYears, contData))
        count = len(contData) * len(years)
        return totalGdp / count if count else 0.0

    return {cont: avgForContinent(cont) for cont in continents}


def calculateGlobalTrend(data: List[Dict], startYear: int, endYear: int) -> Dict[str, float]:
    years = [str(y) for y in range(startYear, endYear + 1)]

    def sumForYear(year: str) -> float:
        def extractYearGdp(countryRecord: dict) -> float:
            return getGdp(countryRecord, year)

        return sum(map(extractYearGdp, data))

    return {y: sumForYear(y) for y in years}


def getRankedContinentGrowth(data: List[Dict], startYear: str, endYear: str) -> List[Dict[str, Any]]:
    continents = getUniqueContinents(data)

    def contGrowth(cont: str) -> float:
        contData = filterByContinent(data, cont)

        def extractStartGdp(countryRecord: dict) -> float:
            return getGdp(countryRecord, startYear)

        def extractEndGdp(countryRecord: dict) -> float:
            return getGdp(countryRecord, endYear)

        startTotal = sum(map(extractStartGdp, contData))
        endTotal = sum(map(extractEndGdp, contData))
        return calculateGrowth(startTotal, endTotal)

    def formatGrowthResult(cont: str) -> Dict[str, Any]:
        return {"Continent": cont, "Growth": contGrowth(cont)}

    growths = list(map(formatGrowthResult, continents))

    def extractGrowthValue(record: dict) -> float:
        return record["Growth"]

    return sorted(growths, key=extractGrowthValue, reverse=True)


def checkConsistentDecline(row: dict, startYear: int, endYear: int) -> bool:
    if startYear >= endYear:
        return False

    def getYearlyGrowth(year: int) -> float:
        return calculateGrowth(getGdp(row, str(year)), getGdp(row, str(year + 1)))

    yoyGrowths = list(map(getYearlyGrowth, range(startYear, endYear)))
    avgGrowth = sum(yoyGrowths) / len(yoyGrowths) if yoyGrowths else 0.0
    return avgGrowth <= 2.0


def getDecliningCountries(data: List[Dict], startYear: int, endYear: int) -> List[str]:
    def isDeclining(countryRecord: dict) -> bool:
        return checkConsistentDecline(countryRecord, startYear, endYear)

    def extractName(countryRecord: dict) -> str:
        return countryRecord["Country Name"]

    declining = filter(isDeclining, data)
    return list(map(extractName, declining))


def calculateContributions(data: List[Dict], startYear: int, endYear: int) -> Dict[str, float]:
    continents = getUniqueContinents(data)
    years = [str(y) for y in range(startYear, endYear + 1)]

    def getGdpForYears(countryRecord: dict) -> float:
        return sum(map(lambda y: getGdp(countryRecord, y), years))

    totalGlobal = sum(map(getGdpForYears, data))

    def contContrib(cont: str) -> float:
        contData = filterByContinent(data, cont)
        contTotal = sum(map(getGdpForYears, contData))
        return (contTotal / totalGlobal) * 100 if totalGlobal else 0.0

    return {cont: contContrib(cont) for cont in continents}


def validateConfig(config: dict, availableYears: List[int], availableContinents: set) -> None:
    continent = config.get("Continent")
    if continent not in availableContinents:
        raise ValueError(f"Continent '{continent}' not found. Available options are these: {', '.join(availableContinents)}")

    start = config.get("StartYear")
    end = config.get("EndYear")
    target = config.get("TargetYear")

    if not isinstance(start, int) or not isinstance(end, int):
        raise TypeError("StartYear and End Year must be whole integers as in the JSON configuration.")

    if start > end:
        raise ValueError(f"Start Year ({start}) cannot be greater than End Year ({end}).")

    if start not in availableYears or end not in availableYears:
        raise ValueError(f"Year range {start}-{end} is out of bounds. Data available from {min(availableYears)} to {max(availableYears)}.")

    if str(target) not in map(str, availableYears):
        raise ValueError(f"TargetYear '{target}' is not present in the dataset.")


class Orchestrator:
    def __init__(self, sink: DataSink, configFile: dict):
        self.sink = sink
        self.config = configFile

    def execute(self, rawData: List[Dict[str, Any]]) -> None:
        countriesOnly = filterCountries(rawData)

        def extractNumericKeys(key: Any) -> bool:
            return str(key).isdigit()

        def convertToInt(key: Any) -> int:
            return int(key)

        yearsAvail = sorted(list(map(convertToInt, filter(extractNumericKeys, countriesOnly[0].keys()))))
        continentsAvail = getUniqueContinents(countriesOnly)

        #validateConfig(self.config, yearsAvail, continentsAvail)

        continent = self.config.get("Continent").title()
        targetYear = str(self.config.get("TargetYear"))
        startYear = self.config.get("StartYear")
        endYear = self.config.get("EndYear")

        #configuring timeline for functions
        if self.config.get("OutputTimeline").lower() == 'range':
            targetYear = str(endYear)
        if self.config.get("OutputTimeline").lower() == "specificyear":
            startYear = endYear = int(targetYear)

        targetContinentData = filterByContinent(countriesOnly, continent)

        results = {
            "Top_10_Countries": getTopBottomtebn(targetContinentData, targetYear, True),
            "Bottom_10_Countries": getTopBottomtebn(targetContinentData, targetYear, False),
            "Growth_Rate_Continent": getGrowthRates(targetContinentData, str(startYear), str(endYear)),
            "Avg_GDP_By_Continent": calculateAvgGdpContinent(countriesOnly, startYear, endYear),
            "Global_GDP_Trend": calculateGlobalTrend(countriesOnly, startYear, endYear),
            "Ranked_Continent_Growth": getRankedContinentGrowth(countriesOnly, str(startYear), str(endYear)),
            "Consistent_Decline_Countries": getDecliningCountries(countriesOnly, startYear, endYear),
            "Continent_Contribution": calculateContributions(countriesOnly, startYear, endYear)
        }

        self.sink.write(results)