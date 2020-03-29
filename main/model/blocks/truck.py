from casymda.blocks import Entity


class Truck(Entity):
    """ drives tours """

    speed = 30 / 3.6  # km/h -> m/s
    geo_icon = "main/visu/img/truck.png"
