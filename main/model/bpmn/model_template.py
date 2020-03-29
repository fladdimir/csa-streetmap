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

        #!model (generated)

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
