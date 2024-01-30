"""This module contains the configuration for the application"""

from typing import Any, Dict
import yaml
import logging


def read_yaml_file(yaml_path: str) -> Dict[str, Any]:
    """Safely convert a yaml file to a dictionary

    Parameters
    ----------
    yaml_path: str
        The path to the yaml file that should be read

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the key-value pairs from the yaml file
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f.read())


HOUSE_FEATURES = read_yaml_file("funda_insights/config/house_features.yaml")

logger = logging.getLogger("funda_insights")
logger.setLevel(logging.INFO)
