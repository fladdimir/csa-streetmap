from main.geo.base.point import Point
from main.visu.geo_web_canvas import GeoWebCanvas


class GeoVisualizer:
    """ keeps track of icon positions """

    def __init__(self, geo_web_canvas: GeoWebCanvas) -> None:
        self.geo_web_canvas = geo_web_canvas

    def animate(
        self,
        obj: object,
        icon_path: str,
        position: Point,
        direction: float,
        now: float,
        text: str,
    ):
        # assert icon existing in img/
        self.geo_web_canvas.set_position(obj, icon_path, position, direction, now, text)

    def destroy(self, obj: object):
        self.geo_web_canvas.destroy(obj)
