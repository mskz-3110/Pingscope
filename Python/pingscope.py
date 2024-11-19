import plotly.graph_objects as pgo
import numpy as np
import datetime as dt
import time
import math
import json
import os
import ping3

class Color:
  def __init__(self, value):
    self.__Value = value
    self.__R, self.__G, self.__B = [int(value[i: i + 2], 16) for i in range(1, 7, 2)]

  @property
  def Value(self):
    return self.__Value

  @property
  def R(self):
    return self.__R

  @property
  def G(self):
    return self.__G

  @property
  def B(self):
    return self.__B

class Stats:
  def __init__(self, values):
    self.__Min = self.__Max = self.__Avg = 0
    if 0 < len(values):
      self.__Min = min(values)
      self.__Max = max(values)
      self.__Avg = round(sum(values) / len(values))

  @property
  def Min(self):
    return self.__Min

  @property
  def Max(self):
    return self.__Max

  @property
  def Avg(self):
    return self.__Avg

class GroupStats:
  def __init__(self, values, groupMaxCount = 0):
    self.__Tick = 1
    self.__Min = []
    self.__Max = []
    self.__Avg = []
    count = len(values)
    if groupMaxCount <= 0:
      groupMaxCount = count
    if count <= groupMaxCount:
      self.__Avg = values
    else:
      self.__Tick = round(len(values) / groupMaxCount)
      for groupValues in np.array_split(values, groupMaxCount):
        stats = Stats(groupValues)
        self.__Min.append(stats.Min)
        self.__Max.append(stats.Max)
        self.__Avg.append(stats.Avg)

  @property
  def Tick(self):
    return self.__Tick

  @property
  def Min(self):
    return self.__Min

  @property
  def Max(self):
    return self.__Max

  @property
  def Avg(self):
    return self.__Avg

class Ping:
  def __init__(self, dst):
    startTime = time.perf_counter()
    roundTripTime = ping3.ping(dst, timeout = 1, unit = "ms")
    self.__ElapsedTime = time.perf_counter() - startTime
    if not roundTripTime:
      self.__RoundTripTime = 1000
      self.__SleepTime = 0
    else:
      self.__RoundTripTime = math.ceil(roundTripTime)
      self.__SleepTime = max(1 - self.__ElapsedTime, 0)

  @property
  def RoundTripTime(self):
    return self.__RoundTripTime

  @property
  def ElapsedTime(self):
    return self.__ElapsedTime

  @property
  def SleepTime(self):
    return self.__SleepTime

  @classmethod
  def Timestamp(self, time = None):
    if time is None:
      time = dt.datetime.now()
    return time.strftime("%y%m%d_%H%M%S")

class PingRank:
  def __init__(self, value = 50):
    self.__Name = PingRank.ToName(value)
    self.__Color = PingRank.ToColor(self.__Name)

  @property
  def Name(self):
    return self.__Name

  @property
  def Color(self):
    return self.__Color

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
  def __init__(self, roundTripTimes = []):
    self.RoundTripTimes = roundTripTimes

  @property
  def RoundTripTimes(self):
    return self.__RoundTripTimes

  @RoundTripTimes.setter
  def RoundTripTimes(self, roundTripTimes):
    self.__RoundTripTimes = tuple(roundTripTimes)
    self.__Stats = Stats(roundTripTimes)

  @property
  def Stats(self):
    return self.__Stats

  def ToFigure(self, xAxisMaxCount = 30, yAxisMaxCount = 30):
    groupStats = GroupStats([0])
    rank = PingRank()
    if 0 < len(self.__RoundTripTimes):
      rank = PingRank(self.__Stats.Avg)
      groupStats = GroupStats(self.__RoundTripTimes, xAxisMaxCount)
    elapsedTimes = []
    for i in range(1, len(groupStats.Avg)):
      elapsedTimes.append(i * groupStats.Tick)
    elapsedTimes.append(len(self.__RoundTripTimes))
    title = """<b>[Pingscope]<br>{rankName}(Avg:{avg}ms Min:{min}ms Max:{max}ms)</b>""".format(rankName = rank.Name, avg = self.__Stats.Avg, min = self.__Stats.Min, max = self.__Stats.Max)
    color = rank.Color
    if groupStats.Tick == 1:
      figure = pgo.Figure(data = [pgo.Scatter(mode = "lines", x = elapsedTimes, y = groupStats.Avg, line = dict(color = color.Value, width = 5))])
    else:
      fillcolor = """rgba({r}, {g}, {b}, 0.15)""".format(r = color.R, g = color.G, b = color.B)
      figure = pgo.Figure(data = [
        pgo.Scatter(showlegend = False, mode = "lines", x = elapsedTimes, y = groupStats.Min, line = dict(color = color.Value, width = 0)),
        pgo.Scatter(showlegend = False, mode = "lines", x = elapsedTimes, y = groupStats.Avg, line = dict(color = color.Value, width = 5), fillcolor = fillcolor, fill = "tonexty"),
        pgo.Scatter(showlegend = False, mode = "lines", x = elapsedTimes, y = groupStats.Max, line = dict(color = color.Value, width = 0), fillcolor = fillcolor, fill = "tonexty"),
      ])
    figure.update_xaxes(tickformat = "d", dtick = groupStats.Tick, linecolor = "black", linewidth = 3, gridcolor = "black", griddash = "dot", mirror = True)
    figure.update_yaxes(tickformat = "d", dtick = 1, linecolor = "black", linewidth = 3, gridcolor = "black", griddash = "dot", mirror = True)
    figure.update_layout(title = dict(text = title, font = dict(color = color.Value, size = 26), x = 0.5),
      xaxis = dict(title = "Elapsed time(sec)"),
      yaxis = dict(title = "Round trip time(ms)", range = [self.__Stats.Min, min(self.__Stats.Min + yAxisMaxCount, self.__Stats.Max)]),
      font = dict(color = "black", size = 14),
      plot_bgcolor = "white")
    return figure

  def SaveImageFile(self, filePath, width = 1600, height = 900):
    self.ToFigure().write_image(filePath, width = width, height = height)

  def LoadPingFile(self, filePath):
    roundTripTimes = []
    with open(filePath) as file:
      while True:
        line = file.readline()
        if not line:
          break
        if not line.startswith("#"):
          roundTripTimes.append(int(line))
    self.RoundTripTimes = roundTripTimes
    return self

  @classmethod
  def OpenWriteFile(cls, filePath):
    directoryPath = os.path.dirname(filePath)
    if not os.path.isdir(directoryPath):
      os.makedirs(directoryPath)
    return open(filePath, mode = "w", newline = "\n")

  @classmethod
  def Run(cls, dst, count = 5, onLine = None):
    startTime = dt.datetime.now()
    if onLine is None:
      onLine = lambda line: None
    onLine("""#{line}\n""".format(line = json.dumps({"Dst": dst, "Count": count, "Timestamp": Ping.Timestamp(startTime)})))
    roundTripTimes = []
    ping = Ping(dst)
    if ping.RoundTripTime < 1000:
      for _ in range(count):
        ping = Ping(dst)
        roundTripTimes.append(ping.RoundTripTime)
        onLine("""{line}\n""".format(line = ping.RoundTripTime))
        time.sleep(ping.SleepTime)
    elapsedTime = int((dt.datetime.now() - startTime).total_seconds())
    stats = Stats(roundTripTimes)
    onLine("""#{line}\n""".format(line = json.dumps({"Avg": stats.Avg, "Min": stats.Min, "Max": stats.Max, "ElapsedTime": elapsedTime})))
    return PingConfig(roundTripTimes)
