from multiprocessing import Value

from casymda.environments.realtime_environment import (
    ChangeableFactorRealtimeEnvironment,
    SyncedFloat,
)
from casymda.visualization.canvas.web_canvas import WebCanvas
from casymda.visualization.process_visualizer import ProcessVisualizer
import casymda.visualization.web_server.flask_sim_server as fss
from casymda.visualization.web_server.sim_controller import RunnableSimulation

from main.model.model import Model
import root_dir

PROCESS_FLOW_SPEED = 20000
WIDTH = 450
HEIGHT = 190
SCALE = 1.0
BACKGROUND_IMAGE = "main/visu/diagram.png"
ENTITY_ICON = "main/visu/simple_entity_icon.png"


class RunnableTourSimProcess(RunnableSimulation):
    def __init__(self):
        self.width, self.height = WIDTH, HEIGHT
        self.root_file = root_dir.__file__

    def simulate(
        self, shared_state: dict, should_run: Value, factor: SyncedFloat
    ) -> None:

        # setup environment
        env = ChangeableFactorRealtimeEnvironment(factor=factor, should_run=should_run)
        model = Model(env)

        web_canvas = WebCanvas(shared_state, self.width, self.height, scale=SCALE)
        process_visualizer = ProcessVisualizer(
            web_canvas,
            flow_speed=PROCESS_FLOW_SPEED,
            background_image_path=BACKGROUND_IMAGE,
            default_entity_icon_path=ENTITY_ICON,
        )

        for block in model.model_graph:
            block.visualizer = process_visualizer

        env.run()


def run_animation():
    rs = RunnableTourSimProcess()
    fss.run_server(rs)
