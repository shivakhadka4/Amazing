import sys
from typing import Dict, Any


def parse_config(file_path: str) -> Dict[str, Any]:
    config: Dict[str, Any] = {}
    mandatory_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(
                        f"Line {line_num}: Invalid syntax (expected KEY=VALUE)"
                    )

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key not in mandatory_keys:
                    pass

                config[key] = value

        for mk in mandatory_keys:
            if mk not in config:
                raise KeyError(f"Missing mandatory configuration key: {mk}")

        config["WIDTH"] = int(config["WIDTH"])
        config["HEIGHT"] = int(config["HEIGHT"])

        entry_parts = config["ENTRY"].split(",")
        config["ENTRY"] = (
            int(entry_parts[0].strip()),
            int(entry_parts[1].strip()),
        )

        exit_parts = config["EXIT"].split(",")
        config["EXIT"] = (
            int(exit_parts[0].strip()),
            int(exit_parts[1].strip()),
        )

        if config["PERFECT"].lower() == "true":
            config["PERFECT"] = True
        elif config["PERFECT"].lower() == "false":
            config["PERFECT"] = False
        else:
            raise ValueError("PERFECT value must be True or False")

        return config

    except Exception as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        sys.exit(1)
