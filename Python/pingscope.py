import plotly.graph_objects as pgo
import numpy as np

class Color:
  def __init__(self, value):
    self._Value = value
    self._R, self._G, self._B = [int(value[i: i + 2], 16) for i in range(1, 7, 2)]

  @property
  def Value(self):
    return self._Value

  @property
  def R(self):
    return self._R

  @property
  def G(self):
    return self._G

  @property
  def B(self):
    return self._B

class Stats:
  def __init__(self, values):
    self._Min = self._Max = self._Avg = 0
    if 0 < len(values):
      self._Min = min(values)
      self._Max = max(values)
      self._Avg = round(sum(values) / len(values))

  @property
  def Min(self):
    return self._Min

  @property
  def Max(self):
    return self._Max

  @property
  def Avg(self):
    return self._Avg

class PingRank:
  def __init__(self, value = 50):
    self._Name = PingRank.ToName(value)
    self._Color = PingRank.ToColor(self._Name)

  @property
  def Name(self):
    return self._Name

  @property
  def Color(self):
    return self._Color

  @classmethod
  def ToName(cls, value):
    if value < 10:
      return "S"
    if value < 15:
      return "A"
    if value < 20:
      return "B"
    if value < 30:
      return "C"
    if value < 50:
      return "D"
    return "E"

  @classmethod
  def ToColor(cls, name):
    if name == "S":
        return Color("#0000FF") # blue
    if name == "A":
        return Color("#87CEEB") # skyblue
    if name == "B":
        return Color("#00FF00") # green
    if name == "C":
        return Color("#FFFF00") # yellow
    if name == "D":
        return Color("#FFA500") # orange
    return Color("#FF0000") # red

class PingConfig:
  def __init__(self, roundTripTimes):
    self._RoundTripTimes = tuple(roundTripTimes)
    self._Stats = Stats(roundTripTimes)

  @property
  def RoundTripTimes(self):
    return self._RoundTripTimes

  @property
  def Stats(self):
    return self._Stats

  def ToFigure(self, xAxisMaxCount = 30, yAxisMaxCount = 30):
    elapsedTimeTick = 1
    rank = PingRank()
    minRoundTripTimes = []
    maxRoundTripTimes = []
    avgRoundTripTimes = [0]
    if 0 < len(self._RoundTripTimes):
      rank = PingRank(self._Stats.Avg)
      avgRoundTripTimes = []
      if len(self._RoundTripTimes) <= xAxisMaxCount:
        for value in self._RoundTripTimes:
          avgRoundTripTimes.append(value)
      else:
        elapsedTimeTick = round(len(self._RoundTripTimes) / xAxisMaxCount)
        for roundTripTimes in np.array_split(self._RoundTripTimes, xAxisMaxCount):
          stats = Stats(roundTripTimes)
          minRoundTripTimes.append(stats.Min)
          maxRoundTripTimes.append(stats.Max)
          avgRoundTripTimes.append(stats.Avg)
    elapsedTimes = []
    for i in range(1, len(avgRoundTripTimes)):
      elapsedTimes.append(i * elapsedTimeTick)
    elapsedTimes.append(len(self._RoundTripTimes))
    title = """<b>[Pingscope]<br>{rankName}(Avg:{avg}ms Min:{min}ms Max:{max}ms)</b>""".format(rankName = rank.Name, avg = self._Stats.Avg, min = self._Stats.Min, max = self._Stats.Max)
    color = rank.Color
    if elapsedTimeTick == 1:
      figure = pgo.Figure(data = [pgo.Scatter(mode = "lines", x = elapsedTimes, y = avgRoundTripTimes, line = dict(color = color.Value, width = 5))])
    else:
      fillcolor = """rgba({r}, {g}, {b}, 0.15)""".format(r = color.R, g = color.G, b = color.B)
      figure = pgo.Figure(data = [
        pgo.Scatter(showlegend = False, mode = "lines", x = elapsedTimes, y = minRoundTripTimes, line = dict(color = color.Value, width = 0)),
        pgo.Scatter(showlegend = False, mode = "lines", x = elapsedTimes, y = avgRoundTripTimes, line = dict(color = color.Value, width = 5), fillcolor = fillcolor, fill = "tonexty"),
        pgo.Scatter(showlegend = False, mode = "lines", x = elapsedTimes, y = maxRoundTripTimes, line = dict(color = color.Value, width = 0), fillcolor = fillcolor, fill = "tonexty"),
      ])
    figure.update_xaxes(tickformat = "d", dtick = elapsedTimeTick, linecolor = "black", linewidth = 3, gridcolor = "black", griddash = "dot", mirror = True)
    figure.update_yaxes(tickformat = "d", dtick = 1, linecolor = "black", linewidth = 3, gridcolor = "black", griddash = "dot", mirror = True)
    figure.update_layout(title = dict(text = title, font = dict(color = color.Value, size = 26), x = 0.5),
      xaxis = dict(title = "Elapsed time(sec)"),
      yaxis = dict(title = "Round trip time(ms)", range = [self._Stats.Min, min(self._Stats.Min + yAxisMaxCount, self._Stats.Max)]),
      font = dict(color = "black", size = 14),
      plot_bgcolor = "white")
    return figure
