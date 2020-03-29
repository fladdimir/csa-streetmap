"""create a casymda model from a bpmn file and a template"""
from casymda.bpmn.bpmn_parser import parse_bpmn as csa_parsing

BPMN_PATH = "main/model/bpmn/diagram.bpmn"
TEMPLATE_PATH = "main/model/bpmn/model_template.py"
JSON_PATH = "main/model/bpmn/_temp_bpmn.json"
MODEL_PATH = "main/model/model.py"


def parse_bpmn():
    """parse_bpmn"""
    csa_parsing(BPMN_PATH, JSON_PATH, TEMPLATE_PATH, MODEL_PATH)


if __name__ == "__main__":
    parse_bpmn()
