import hashlib
import os
import pickle
from typing import Dict, List, Tuple

import networkx as nx
import osmnx as ox
import pandas as pd

from main.geo.base.point import Point
from main.geo.base.segment import Segment


class RouteInfo:
    def __init__(self, segments: List[Segment]) -> None:
        self.segments = segments
        self.length = segments[-1].length_end


class GeoInfo:
    def __init__(self) -> None:
        self._route_infos: Dict[str, Dict[str, RouteInfo]]
        self._node_points: Dict[str, Point] = {}
        self._node_descriptions: Dict[str, str] = {}

    def set_route_infos(self, route_infos: Dict[str, Dict[str, RouteInfo]]):
        self._route_infos = route_infos
        nodes = list(self._route_infos.keys())
        for node in nodes:
            other_node = next(o for o in nodes if o is not node)
            self._node_points[node] = (
                self._route_infos[node][other_node].segments[0].start
            )

    def get_nodes(self) -> List[str]:
        return list(self._node_points.keys())

    def get_distance(self, from_node: str, to_node: str) -> float:
        return self._route_infos[from_node][to_node].length

    def get_node_coordinates(self, node: str) -> Point:
        return self._node_points[node]

    def get_node_description(self, node: str) -> str:
        return self._node_descriptions[node]

    def get_segments(self, from_node: str, to_node: str) -> List[Segment]:
        return self._route_infos[from_node][to_node].segments


def init(
    nodes_csv_path: str,
    center: Tuple[float, float],
    distance: float,
    network_type="drive",
) -> GeoInfo:

    h = create_hash(
        get_file_hash(nodes_csv_path) + get_graph_hash(center, distance, network_type)
    )
    cache_dir = get_cache_dir(nodes_csv_path)
    cache_path = cache_dir + "/_temp_" + h + ".pickle"
    try:
        with open(cache_path, "rb") as f:
            geo_info = pickle.load(f)
    except FileNotFoundError:
        geo_info = _init_geo_info(nodes_csv_path, center, distance, network_type)
        with open(cache_path, "wb+") as f:
            pickle.dump(geo_info, f)
    return geo_info


def _init_geo_info(
    nodes_csv_path: str,
    center: Tuple[float, float],
    distance: float,
    network_type="drive",
) -> GeoInfo:
    geo_info = GeoInfo()

    G = load_graph(nodes_csv_path, center, distance, network_type)
    od_nodes = load_nodes_csv(nodes_csv_path, G)

    names = {}
    descriptions = {}
    for node in od_nodes.index:
        names[od_nodes.loc[node]["osm_id"]] = node
        descriptions[node] = od_nodes.loc[node]["description"]
    geo_info._node_descriptions = descriptions

    relevant_node_ids = od_nodes["osm_id"]
    # all possibly relevant shortest paths
    route_infos: Dict[str, Dict[str, RouteInfo]] = {}
    for from_node in relevant_node_ids:
        route_infos[names[from_node]] = {}
        for to_node in relevant_node_ids:
            if from_node != to_node:
                # possible optimization: multi-target
                route = nx.shortest_path(G, from_node, to_node, weight="length")

                # calc segments
                segments: List[Segment] = []
                dist_acc = 0.0
                for i in range(len(route) - 1):
                    start_osm_id = route[i]
                    start_g = G._node[start_osm_id]
                    start = Point(start_g["y"], start_g["x"])

                    end_osm_id = route[i + 1]
                    end_g = G._node[end_osm_id]
                    end = Point(end_g["y"], end_g["x"])

                    segment = Segment(start, end, dist_acc)
                    dist_acc += segment.length
                    segments.append(segment)

                route_infos[names[from_node]][names[to_node]] = RouteInfo(segments)

    geo_info.set_route_infos(route_infos)
    return geo_info


def load_graph(nodes_csv_path, center, distance, network_type):
    file_h = get_graph_hash(center, distance, network_type)
    file_name = "_temp_" + file_h + ".graphml"
    cache_dir = get_cache_dir(nodes_csv_path)

    try:
        return ox.load_graphml(file_name, folder=cache_dir)
    except FileNotFoundError:
        G = ox.graph_from_point(
            center, distance=distance, simplify=False, network_type=network_type
        )
        ox.save_graphml(G, filename=file_name, folder=cache_dir)
        return G


def load_nodes_csv(nodes_csv_path, graph) -> pd.DataFrame:
    with open(nodes_csv_path, "r") as f:
        inp = f.read()
    file_h = create_hash(inp)
    cache_dir = get_cache_dir(nodes_csv_path)
    cache_path = cache_dir + "/_temp_" + file_h + ".csv"
    index_col = "node"
    try:
        return pd.read_csv(cache_path, index_col=index_col)
    except FileNotFoundError:
        df = pd.read_csv(nodes_csv_path, index_col=index_col)
        add_nearest_osm_nodes(graph, df)
        df.to_csv(cache_path)
        return df


def get_cache_dir(nodes_csv_path) -> str:
    cache_dir = os.path.dirname(nodes_csv_path) + "/cache"
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_graph_hash(center, distance, network_type):
    inp = str(center) + str(distance) + network_type
    return create_hash(inp)


def get_file_hash(file_path):
    with open(file_path, "r") as f:
        inp = f.read()
    return create_hash(inp)


def create_hash(s):
    b = str.encode(s)
    h = hashlib.md5(b)
    return h.hexdigest()[:6]


def add_nearest_osm_nodes(graph, df: pd.DataFrame):
    osm_nodes = ox.get_nearest_nodes(graph, df["lon"], df["lat"])
    df.insert(3, "osm_id", osm_nodes)


def draw_graph(nodes_csv_path, center, distance, network_type):
    """ plots graph with relevant nodes """
    G = load_graph(nodes_csv_path, center, distance, network_type)
    od_nodes = load_nodes_csv(nodes_csv_path, G)

    g_nodes = list(G.nodes().keys())
    nc = ["#336699" for _ in g_nodes]
    node_size = [75 for _ in g_nodes]
    for odn in od_nodes["osm_id"]:
        idx = g_nodes.index(odn)
        nc[idx] = "r"
        node_size[idx] = 150
    assert "r" in nc

    ox.plot_graph(G, node_color=nc, node_zorder=3, node_alpha=0.5, node_size=node_size)
