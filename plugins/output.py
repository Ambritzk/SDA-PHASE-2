import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec
from typing import Dict, Any, List
import math


def dataFormat(num: float, pos=None) -> str:
    if num == 0: return "0.0"

    # magnitude by log
    magnitude = int(math.floor(math.log(abs(num), 1000)))

    # Clamp magnitude
    units = ['', 'K', 'M', 'B', 'T']
    magnitude = max(0, min(magnitude, len(units) - 1))

    scaledNum = num / (1000.0 ** magnitude)
    return '%.1f%s' % (scaledNum, units[magnitude])


def formatUnit(key: str, value: Any) -> str:
    if not isinstance(value, (int, float)):
        return str(value)
    if "Growth" in key or "Contribution" in key:
        return f"{value:.2f}%"
    return f"${dataFormat(value)}"


def generateArc(startAngle: float, endAngle: float, arcRadius: float = 1.5) -> np.ndarray:
    # 1. Line OUT
    radiusOfOutside = np.linspace(0, arcRadius, 20)
    lineOfOutside = radiusOfOutside * np.exp(1j * np.full_like(radiusOfOutside, startAngle))

    # 2. Arc
    # not do division by zero if angle is 0
    angleDiff = endAngle - startAngle
    arcPoints = int(50 * (angleDiff / (2 * np.pi))) + 10
    thetaArc = np.linspace(startAngle, endAngle, arcPoints)
    arcCurve = arcRadius * np.exp(1j * thetaArc)

    # 3. Line IN
    radiusIn = np.linspace(arcRadius, 0, 20)
    lineIn = radiusIn * np.exp(1j * np.full_like(radiusIn, endAngle))

    return np.concatenate([lineOfOutside, arcCurve, lineIn])


def calculateRadiiValues(values: List[float]) -> np.ndarray:
    totalSum = sum(values)
    if totalSum == 0: return np.array([])

    # Calculate angles
    fractions = np.array(values) / totalSum
    angles = fractions * 2 * np.pi

    # Create cummulative start and end angles [0, a1, a1+a2, ...]
    boundaries = np.concatenate(([0], np.cumsum(angles)))
    initAngles = boundaries[:-1]
    endAngles = boundaries[1:]

    # Map segment over angle pairs
    segments = map(generateArc, initAngles, endAngles)
    return np.concatenate(list(segments))


def executeFftAlgorithm(complexPath: np.ndarray, limit: int = None) -> tuple:
    dataLength = len(complexPath)
    coeffs = np.fft.fft(complexPath) / dataLength
    freqs = np.fft.fftfreq(dataLength)

    # Sort by amplitude
    sortIdx = np.argsort(np.abs(coeffs))[::-1]
    sortedCoefficients = coeffs[sortIdx]
    sortedFrequencies = freqs[sortIdx]

    # Apply limit
    return (sortedCoefficients[:limit], sortedFrequencies[:limit], dataLength) if limit else (sortedCoefficients,
                                                                                              sortedFrequencies,
                                                                                              dataLength)


def circularRadiusValues(years: List[int], gdpValues: List[float]) -> tuple:
    # numpy nd array for immutable work
    xRaw = np.array(years, dtype=float)
    yRaw = np.array(gdpValues, dtype=float)

    # data range(prevention of divide by zero for miniscule change)
    xRange = (xRaw.max() - xRaw.min()) + 1e-9
    yRange = (yRaw.max() - yRaw.min()) + 1e-9

    # Linear scaling of data for centering
    xNorm = 4 * (xRaw - xRaw.min()) / xRange - 2
    yNorm = 3 * (yRaw - yRaw.min()) / yRange - 1.5

    # Create Path (Forward & Backward)
    xPath = np.concatenate([xNorm, xNorm[::-1]])
    yPath = np.concatenate([yNorm, yNorm[::-1]])
    complexPath = xPath + 1j * yPath

    coeffs, freqs, dataLength = executeFftAlgorithm(complexPath, limit=150)
    return coeffs, freqs, dataLength, xRaw, yRaw


def pieChartValues(labels: List[str], values: List[float]) -> tuple:
    complexPath = calculateRadiiValues(values)
    numCircles = min(300, len(complexPath))
    coefficients, frequencies, dataLength = executeFftAlgorithm(complexPath, limit=numCircles)
    return coefficients, frequencies, dataLength, labels, values


def getLabelPositions(values: List[float], chartRadius: float = 2.0) -> List[tuple]:
    totalSum = sum(values)
    if totalSum == 0: return []

    # Vectorized calculation of mid-angles
    cumulative = np.cumsum(values)
    boundaries = np.concatenate(([0], cumulative))
    midPoints = (boundaries[:-1] + boundaries[1:]) / 2
    midAngles = (midPoints / totalSum) * 2 * np.pi

    # polar to cartesian
    return [(chartRadius * np.cos(theta), chartRadius * np.sin(theta)) for theta in midAngles]


class ConsoleWriter:
    def write(self, records: Dict[str, Any]) -> None:
        def formatDictionaryPart(keyValuePair: tuple, parentKey: str) -> str:
            childKey, childValue = keyValuePair
            return f"{childKey}: {formatUnit(parentKey, childValue)}"

        def printListItem(parentKey: str, item: Any) -> None:
            if isinstance(item, dict):
                formattedParts = map(lambda kv: formatDictionaryPart(kv, parentKey), item.items())
                print("  - " + ", ".join(list(formattedParts)))
            else:
                print(f"  - {item}")

        def printDictionaryItem(keyValuePair: tuple, parentKey: str) -> None:
            childKey, childValue = keyValuePair
            print(f"  {childKey}: {formatUnit(parentKey, childValue)}")

        def processRecord(keyValuePair: tuple) -> None:
            key, value = keyValuePair
            print()
            print(f"[{key.upper().replace('_', ' ')}]")

            if isinstance(value, list):
                list(map(lambda item: printListItem(key, item), value))
            elif isinstance(value, dict):
                list(map(lambda kv: printDictionaryItem(kv, key), value.items()))
            else:
                print(f"  {value}")

        list(map(processRecord, records.items()))


class GraphicsChartWriter:
    def __init__(self):
        self.animations = []

    def write(self, records: Dict[str, Any]) -> None:
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(16, 10), facecolor='#111111')
        gs = GridSpec(2, 2, figure=fig)

        axGrowth = fig.add_subplot(gs[0, 0], facecolor='#111111')
        axPie = fig.add_subplot(gs[0, 1], facecolor='#111111')
        axTop10 = fig.add_subplot(gs[1, 0], facecolor='#111111')
        axBottom10 = fig.add_subplot(gs[1, 1], facecolor='#111111')

        trend = records.get("Global_GDP_Trend", {})
        if trend:
            self.setupGrowthCurve(axGrowth, fig, list(trend.keys()), list(trend.values()), "Total Global GDP Trend ($)")

        contrib = records.get("Continent_Contribution", {})
        if contrib:
            self.setupPieChart(axPie, fig, list(contrib.keys()), list(contrib.values()),
                               "Contribution to Global GDP (%)")

        top10 = records.get("Top_10_Countries", [])
        if top10:
            self.setupBarChart(axTop10, [item["Country"] for item in top10], [item["GDP"] for item in top10],
                               "Top 10 Countries", "cyan")

        bottom10 = records.get("Bottom_10_Countries", [])
        if bottom10:
            self.setupBarChart(axBottom10, [item["Country"] for item in bottom10], [item["GDP"] for item in bottom10],
                               "Bottom 10 Countries", "orange")

        plt.tight_layout()
        plt.show()

    def setupBarChart(self, ax, names: List[str], vals: List[float], title: str, color: str) -> None:
        ax.bar(names, vals, color=color, label=f"GDP Metrics ($)")
        ax.set_title(title.upper(), color='red', fontsize=14)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(dataFormat))
        ax.tick_params(axis='x', rotation=45, colors='white', labelsize=9)
        ax.tick_params(axis='y', colors='white')

        def styleSpine(spine) -> None:
            spine.set_color('white')

        list(map(styleSpine, ax.spines.values()))
        ax.legend(loc='upper right', facecolor='#111111', edgecolor='white', labelcolor='white')

    def setupGrowthCurve(self, ax, fig, yearsStr: List[str], gdpValues: List[float], title: str) -> None:
        years = [int(y) for y in yearsStr]
        coeffs, freqs, frameCount, xRaw, yRaw = circularRadiusValues(years, gdpValues)

        ax.set_title(title.upper(), color='red', fontsize=14)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-2.5, 2.5)

        realYears = np.linspace(xRaw.min(), xRaw.max(), 6)
        ax.set_xticks(np.linspace(-2, 2, 6))
        ax.set_xticklabels(realYears.astype(int), color='white')

        realGdp = np.linspace(yRaw.min(), yRaw.max(), 5)
        ax.set_yticks(np.linspace(-1.5, 1.5, 5))
        ax.set_yticklabels([f"${dataFormat(v)}" for v in realGdp], color='white')

        traceLine, = ax.plot([], [], color='red', lw=2, label="Calculated Global Trend ($)")
        armsLine, = ax.plot([], [], color='white', alpha=0.3, lw=0.4)
        circles = [ax.plot([], [], color='white', alpha=0.1, lw=0.2)[0] for _ in range(len(coeffs))]
        drawingTip, = ax.plot([], [], 'mo', markersize=2)

        ax.legend(loc='upper left', facecolor='#111111', edgecolor='white', labelcolor='white')

        def updateFrame(frame):
            exponents = np.exp(2j * np.pi * freqs * frame)
            positions = np.insert(np.cumsum(coeffs * exponents), 0, 0 + 0j)
            theta = np.linspace(0, 2 * np.pi, 20)

            def updateCirclePosition(item: tuple) -> None:
                index, circle = item
                center = positions[index]
                circleRadius = np.abs(coeffs[index])
                circle.set_data(center.real + circleRadius * np.cos(theta), center.imag + circleRadius * np.sin(theta))

            list(map(updateCirclePosition, enumerate(circles)))

            armsLine.set_data(positions.real, positions.imag)
            tip = positions[-1]

            currentX = list(traceLine.get_xdata()) if frame != 0 else []
            currentY = list(traceLine.get_ydata()) if frame != 0 else []

            # Stop drawing after first pass
            newX = currentX + [tip.real] if frame <= frameCount / 2 + 5 else currentX
            newY = currentY + [tip.imag] if frame <= frameCount / 2 + 5 else currentY

            traceLine.set_data(newX, newY)
            drawingTip.set_data([tip.real], [tip.imag])
            return [traceLine, armsLine, drawingTip] + circles

        ani = FuncAnimation(fig, updateFrame, frames=frameCount, interval=10, blit=True)
        self.animations.append(ani)

    def setupPieChart(self, ax, fig, labels: List[str], values: List[float], title: str) -> None:
        coeffs, freqs, frameCount, lbls, vals = pieChartValues(labels, values)
        labelCoords = getLabelPositions(vals, chartRadius=1.8)

        ax.set_xlim(-5, 5)
        ax.set_ylim(-3.5, 3.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title.upper(), color='yellow', fontsize=14)

        traceLine, = ax.plot([], [], color='red', lw=2)
        armsLine, = ax.plot([], [], color='white', alpha=0.3, lw=0.8)
        circles = [ax.plot([], [], color='white', alpha=0.05, lw=0.8)[0] for _ in range(len(coeffs))]
        penPoint, = ax.plot([], [], 'mo', markersize=6)

        def drawChartText(dataItem: tuple) -> None:
            coords, labelText, val = dataItem
            lx, ly = coords
            ha = 'left' if lx > 0 else 'right'
            va = 'bottom' if ly > 0 else 'top'
            ax.text(lx, ly, labelText, color='yellow', fontsize=8, ha=ha, va=va)

        def drawLegendEntry(dataItem: tuple) -> None:
            labelText, val = dataItem
            ax.plot([], [], marker='o', color='white', markersize=6, linestyle='None', label=f"{labelText}: {val:.2f}%")

        list(map(drawChartText, zip(labelCoords, lbls, vals)))
        list(map(drawLegendEntry, zip(lbls, vals)))

        ax.legend(loc='upper right', facecolor='#111111', edgecolor='white', labelcolor='white', fontsize=8)

        def updateFrame(frame):
            exponents = np.exp(2j * np.pi * freqs * frame)
            terms = coeffs * exponents
            positions = np.insert(np.cumsum(terms), 0, 0 + 0j)
            theta = np.linspace(0, 2 * np.pi, 20)

            def updateCirclePosition(item: tuple) -> None:
                index, circle = item
                center = positions[index]
                circleRadius = np.abs(coeffs[index])
                circle.set_data(center.real + circleRadius * np.cos(theta), center.imag + circleRadius * np.sin(theta))

            list(map(updateCirclePosition, enumerate(circles)))

            armsLine.set_data(positions.real, positions.imag)
            tip = positions[-1]

            currentX = list(traceLine.get_xdata()) if frame != 0 else []
            currentY = list(traceLine.get_ydata()) if frame != 0 else []

            newX = currentX + [tip.real]
            newY = currentY + [tip.imag]

            traceLine.set_data(newX, newY)
            penPoint.set_data([tip.real], [tip.imag])
            return [traceLine, armsLine, penPoint] + circles

        ani = FuncAnimation(fig, updateFrame, frames=frameCount, interval=5, blit=True)
        self.animations.append(ani)