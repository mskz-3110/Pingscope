import pingscope as ps

def test_OutputPng():
  width = 1600
  height = 900
  ps.PingConfig([7, 8, 9, 10, 11]).ToFigure().write_image("../Image/SampleS.png", width = width, height = height)
  ps.PingConfig([12, 13, 14, 15, 16]).ToFigure().write_image("../Image/SampleA.png", width = width, height = height)
  ps.PingConfig([17, 18, 19, 20, 21]).ToFigure().write_image("../Image/SampleB.png", width = width, height = height)
  ps.PingConfig([27, 28, 29, 30, 31]).ToFigure().write_image("../Image/SampleC.png", width = width, height = height)
  ps.PingConfig([47, 48, 49, 50, 51]).ToFigure().write_image("../Image/SampleD.png", width = width, height = height)
  ps.PingConfig([48, 49, 1000, 51, 52]).ToFigure().write_image("../Image/SampleE.png", width = width, height = height)
  ps.PingConfig([]).ToFigure().write_image("../Image/Sample0.png", width = width, height = height)

  roundTripTimes = []
  for i in range(3600):
    roundTripTimes.append(i % 30 + 10)
  ps.PingConfig(roundTripTimes).ToFigure().write_image("../Image/Sample3600.png", width = width, height = height)
