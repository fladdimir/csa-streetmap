"""simple example including visualization"""
import os
from tkinter import Tk

from casymda.visualization.canvas.tk_canvas import ScaledCanvasTk
from casymda.visualization.process_visualizer import ProcessVisualizer
from simpy import Environment

from main.model.model import Model


def test_tk_process_visualization(flow_speed=1e6):
    """test visualized run"""
    if os.name != "nt" and os.environ.get("DISPLAY", "") == "":
        print("no display, animated run pointless (e.g. inside a container)")
        # (this check for DISPLAY does not work on win)
        return

    env = Environment()
    model = Model(env)

    width = 451
    height = 212
    gui = Tk()
    canvas = ScaledCanvasTk(gui, width, height)

    visualizer = ProcessVisualizer(
        canvas,
        flow_speed=flow_speed,
        background_image_path="main/visu/diagram.png",
        default_entity_icon_path="main/visu/simple_entity_icon.png",
    )

    for block in model.model_components.values():
        block.visualizer = visualizer

    env.run()
    gui.destroy()

    assert env.now > 0
