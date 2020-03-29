class Point:
    def __init__(self, lat: float, lon: float) -> None:
        self.lat = lat
        self.lon = lon

    def to_string(self):
        return "lat: %f - lon: %f" % (self.lat, self.lon)
