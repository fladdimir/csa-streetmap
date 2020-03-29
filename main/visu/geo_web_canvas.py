from typing import Dict
from main.geo.base.point import Point


class GeoWebCanvas:
    def __init__(self, shared_state: Dict) -> None:
        self.dict = shared_state  # flat (shareable), json-serializable dict
        self.last_update = -1

    def set_position(
        self,
        obj: object,
        icon_path: str,
        position: Point,
        direction: float,  # clockwise from Y-axis (deg)
        now: float,
        text: str,
    ):
        self.dict[id(obj)] = {
            "icon_path": icon_path,
            "lat": position.lat,
            "lon": position.lon,
            "direction": direction,
            "text": text,
        }
        self.last_update = now

    def destroy(self, obj: object):
        del self.dict[id(obj)]
