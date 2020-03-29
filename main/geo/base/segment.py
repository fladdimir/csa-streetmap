import numpy as np
import osmnx as ox

from main.geo.base.point import Point


class Segment:
    """ holds precalculated infos for animation along multiple segments """

    def __init__(self, start: Point, end: Point, length_start: float) -> None:
        self.start = start
        self.end = end
        self.length_start = length_start

        self.length: float = ox.great_circle_vec(start.lat, start.lon, end.lat, end.lon)
        self.length_end = self.length_start + self.length
        self.vector = Point(
            lat=self.end.lat - self.start.lat, lon=self.end.lon - self.start.lon
        )
        self.direction = self.calc_direction(start, end)

    def calc_direction(self, start: Point, end: Point) -> float:
        dx = ox.great_circle_vec(start.lat, start.lon, start.lat, end.lon) * np.sign(
            end.lon - start.lon
        )

        dy = ox.great_circle_vec(start.lat, start.lon, end.lat, start.lon) * np.sign(
            end.lat - start.lat
        )

        return np.arctan2(dx, dy) * 180 / np.pi
