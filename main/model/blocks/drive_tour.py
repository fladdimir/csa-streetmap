from typing import Any, List, Optional, cast

from casymda.blocks.block_components import VisualizableBlock
import simpy

from main.geo.base.point import Point
from main.geo.base.segment import Segment
from main.geo.geo_info import GeoInfo
from main.model.blocks.truck import Truck
from main.visu.geo_visualizer import GeoVisualizer


class DriveTour(VisualizableBlock):

    NODE_ICON = "main/visu/img/node.png"

    UNLOADING_TIME = 10

    animation_timestep = 1

    def __init__(
        self,
        env,
        name,
        block_capacity=float("inf"),
        xy=(0, 0),
        ways={},
        geo_info: GeoInfo = None,
        start: str = "",
        stops: List[str] = [],
    ):
        super().__init__(env, name, block_capacity=block_capacity, xy=xy, ways=ways)

        if geo_info is None:
            raise AssertionError("geo_info must not be None")
        self.geo_info: GeoInfo = cast(GeoInfo, geo_info)
        self.start = start
        self.stops = stops
        self.stops.append(start)  # always return to start

        self.geo_visualizer: Optional[GeoVisualizer] = None

    def actual_processing(self, entity: Truck):
        truck_position = self.start

        for next_stop in self.stops:
            distance = self.geo_info.get_distance(truck_position, next_stop)
            driving_time = distance / entity.speed

            animation = self.setup_animation(
                entity,
                from_node=truck_position,
                to_node=next_stop,
                destroy_on_arrival=(next_stop == self.stops[-1]),
            )  # (could be expressable using with)
            yield self.env.timeout(driving_time)  # simulate driving time
            if animation is not None:
                animation.interrupt()

            truck_position = next_stop  # arrival
            yield self.env.timeout(self.UNLOADING_TIME)

    # animation-related behavior:

    def set_geo_visualizer(self, visualizer: GeoVisualizer):
        self.geo_visualizer = visualizer
        self.animate_nodes()

    def setup_animation(
        self, entity: Truck, from_node: str, to_node: str, destroy_on_arrival=False
    ) -> Any:
        """ returns interruptable simpy process (or None) """
        if self.geo_visualizer is None:
            return None
        else:
            return self.env.process(
                self.animation(entity, from_node, to_node, destroy_on_arrival)
            )

    def animation(
        self, entity: Truck, from_node: str, to_node: str, destroy_on_arrival: bool
    ):
        try:
            segments = self.geo_info.get_segments(from_node, to_node)
            current_segment_idx = 0
            time_spent = 0
            while True:
                current_segment_idx = self.animate_progress(
                    entity, segments, time_spent, current_segment_idx
                )
                self.adjust_animation_timestep()
                yield self.env.timeout(self.animation_timestep)
                time_spent += self.animation_timestep
        except simpy.Interrupt:
            pass  # arrival
        finally:
            if destroy_on_arrival:
                self.geo_visualizer.destroy(entity)

    def animate_progress(
        self, entity: Truck, segments: List[Segment], time_spent: float, segm_idx: int,
    ) -> int:
        distance = entity.speed * time_spent
        while segments[segm_idx].length_end < distance and segm_idx < len(segments):
            segm_idx += 1
        segment = segments[segm_idx]
        progress = min((distance - segment.length_start) / segment.length, 1)
        position = self.calculate_position(segment.start, progress, segment.vector)

        self.geo_visualizer.animate(
            entity, entity.geo_icon, position, segment.direction, self.env.now, "Truck"
        )
        return segm_idx

    def calculate_position(self, start: Point, progress: float, vector: Point):
        # simplified as cartesian coordinates
        lat = start.lat + vector.lat * progress
        lon = start.lon + vector.lon * progress
        return Point(lat=lat, lon=lon)

    def adjust_animation_timestep(self):
        if hasattr(self.env, "factor"):
            FPS = 25
            self.animation_timestep = (1 / FPS) / self.env.factor

    def animate_nodes(self):
        for node in self.geo_info.get_nodes():
            pos = self.geo_info.get_node_coordinates(node)
            self.geo_visualizer.animate(
                node,
                self.NODE_ICON,
                pos,
                0,
                self.env.now,
                self.geo_info.get_node_description(node),
            )
