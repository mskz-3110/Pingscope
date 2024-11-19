import pingscope as ps

def test_OutputPng():
  ps.PingConfig([7, 8, 9, 10, 11]).SaveImageFile("../Image/SampleS.png")
  ps.PingConfig([12, 13, 14, 15, 16]).SaveImageFile("../Image/SampleA.png")
  ps.PingConfig([17, 18, 19, 20, 21]).SaveImageFile("../Image/SampleB.png")
  ps.PingConfig([27, 28, 29, 30, 31]).SaveImageFile("../Image/SampleC.png")
  ps.PingConfig([47, 48, 49, 50, 51]).SaveImageFile("../Image/SampleD.png")
  ps.PingConfig([48, 49, 1000, 51, 52]).SaveImageFile("../Image/SampleE.png")
  ps.PingConfig([]).SaveImageFile("../Image/Sample0.png")

  roundTripTimes = []
  for i in range(3600):
    roundTripTimes.append(i % 30 + 10)
  ps.PingConfig(roundTripTimes).SaveImageFile("../Image/Sample3600.png")

#def test_Ping():
#  pingFilePath = """../Image/{timestamp}.ping""".format(timestamp = ps.Ping.Timestamp())
#  with ps.PingConfig.OpenWriteFile(pingFilePath) as file:
#    ps.PingConfig.Run("localhost", onLine = lambda line: file.write(line)).SaveImageFile("../Image/PingSave.png")
#  ps.PingConfig().LoadPingFile(pingFilePath).SaveImageFile("../Image/PingLoad.png")
