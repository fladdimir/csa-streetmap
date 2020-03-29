import pytest
from simpy import Environment

from main.geo.geo_info import GeoInfo
from main.model.blocks.truck import Truck
from main.model.bpmn.generate_model import parse_bpmn
from main.model.model import Model
from main.visu.geo_visualizer import GeoVisualizer
from main.visu.geo_web_canvas import GeoWebCanvas


def test_model_generation():
    parse_bpmn()
    from main.model.model import Model

    assert Model(Environment()) is not None


def test_model_execution():
    env = Environment()
    model = Model(env)
    env.run()
    assert model.sink.overall_count_in == model.source.max_entities


def test_model_driving_time():
    class FakeGeoInfo(GeoInfo):
        distance = 1

        def get_distance(self, from_node, to_node):
            return self.distance

    env = Environment()
    model = Model(env)

    model.source.max_entities = 1
    model.drive_tour.geo_info = FakeGeoInfo()

    env.run()

    num_drives = len(model.drive_tour.stops)
    overall_distance = num_drives * FakeGeoInfo.distance
    driving_time = overall_distance / Truck.speed
    unloading_time = model.drive_tour.UNLOADING_TIME * num_drives
    tour_duration = unloading_time + driving_time
    assert env.now == pytest.approx(tour_duration)


def test_model_execution_geo_visualizer():
    env = Environment()
    model = Model(env)
    env.run()
    time_without_visualizer = env.now

    env = Environment()
    model = Model(env)

    canvas_dict = {}
    geo_canvas = GeoWebCanvas(canvas_dict)
    geo_visualizer = GeoVisualizer(geo_canvas)
    model.drive_tour.set_geo_visualizer(geo_visualizer)

    env.run()
    time_with_visualizer = env.now
    assert model.sink.overall_count_in == model.source.max_entities
    assert time_with_visualizer == time_without_visualizer
