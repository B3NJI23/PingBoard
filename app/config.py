from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).parent.parent / "targets.yaml"

def load_targets() -> list[dict]:
    with open(CONFIG_PATH) as file:
        data = yaml.safe_load(file)

    return data["targets"]