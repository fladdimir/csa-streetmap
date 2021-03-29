from typing import Any, Dict, List
from casymda.blocks import Sink, Source

from main.geo.geo_info import GeoInfo
from main.model.blocks.drive_tour import DriveTour
from main.model.blocks.truck import Truck
from main.model.geo_info_setup import get_geo_info

geo_info: GeoInfo = get_geo_info()


class Model:
    def __init__(self, env):

        self.env = env
        self.model_components: Any
        self.model_graph_names: Dict[str, List[str]]

        #!resources+components (generated)

        self.source = Source(
            self.env,
            "source",
            xy=(79, 59),
            entity_type=Truck,
            max_entities=10,
            inter_arrival_time=50,
            ways={"drive_tour": [(97, 59), (180, 59)]},
        )

        self.sink = Sink(self.env, "sink", xy=(368, 59), ways={})

        self.drive_tour = DriveTour(
            self.env,
            "drive_tour",
            xy=(230, 59),
            geo_info=geo_info,
            start="PAT",
            stops=[["ZFB", "MMC", "CAV"], ["CAV", "MMC", "ZFB"]],
            ways={"sink": [(280, 59), (350, 59)]},
        )

        #!model (generated)

        self.model_components = {
            "source": self.source,
            "sink": self.sink,
            "drive_tour": self.drive_tour,
        }

        self.model_graph_names = {
            "source": ["drive_tour"],
            "sink": [],
            "drive_tour": ["sink"],
        }
        # translate model_graph_names into corresponding objects
        self.model_graph = {
            self.model_components[name]: [
                self.model_components[nameSucc]
                for nameSucc in self.model_graph_names[name]
            ]
            for name in self.model_graph_names
        }

        for component in self.model_graph:
            component.successors = self.model_graph[component]
