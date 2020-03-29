from main.geo.geo_info import GeoInfo, init, draw_graph

NODES_CSV_PATH = "main/geo/nodes.csv"
CENTER = (53.55668, 9.92815)
DISTANCE = 300
NETWORK_TYPE = "drive"


def get_geo_info() -> GeoInfo:
    return init(
        nodes_csv_path=NODES_CSV_PATH,
        center=CENTER,
        distance=DISTANCE,
        network_type=NETWORK_TYPE,
    )


def plot_graph():
    draw_graph(NODES_CSV_PATH, CENTER, DISTANCE, NETWORK_TYPE)
