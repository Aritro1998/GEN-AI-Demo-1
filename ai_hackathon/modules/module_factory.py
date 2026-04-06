from modules.base_module import BaseModule
from modules.classifier import Classifier
from modules.generator import Generator
from modules.reasoner import Reasoner


MODULE_TYPES = {
    "base": BaseModule,
    "classifier": Classifier,
    "reasoner": Reasoner,
    "generator": Generator,
}


def create_module(module_type):
    if module_type not in MODULE_TYPES:
        available = ", ".join(sorted(MODULE_TYPES))
        raise ValueError(
            f"Unknown module type '{module_type}'. Available module types: {available}"
        )

    return MODULE_TYPES[module_type]()
