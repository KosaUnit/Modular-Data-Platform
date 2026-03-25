import json
from pathlib import Path


class ConfigLoader:
    """
    Loads and provides access to the event schema configuration.
    """

    def __init__(self, config_path: str):
        """
        Args:
            config_path: Path to the JSON schema file.
            
        Raises:
            FileNotFoundError: If the config file doesn't exist.
            KeyError: If required sections are missing from the config.
        """
        self._raw_config = self._load_config(config_path)
        self._build_lookup_tables()

    # Loading 

    def _load_config(self, config_path: str) -> dict:
        """
        Reads the JSON file and returns it as a Python dictionary.
        
        Path is a standard library class that handles file paths
        across operating systems (Windows uses \\, Linux uses /).
        """
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Config file not found: {path.absolute()}"
            )

        with open(path, "r") as file:
            return json.load(file)



    # Building Lookup Tables 

    def _build_lookup_tables(self):
        """
        Pre-computes lists and weights from the config for fast access.
        """
        # ── Event Types ──
        self.event_types = list(self._raw_config["event_types"].keys())
        self.event_type_weights = [
            self._raw_config["event_types"][et]["weight"]
            for et in self.event_types
        ]

        # ── Statuses ──
        self.statuses = list(self._raw_config["statuses"].keys())
        self.status_weights = [
            self._raw_config["statuses"][s]["weight"]
            for s in self.statuses
        ]

        # ── Device Types ──
        self.device_types = list(self._raw_config["device_types"].keys())
        self.device_type_weights = [
            self._raw_config["device_types"][d]["weight"]
            for d in self.device_types
        ]

        # ── Connection Types ──
        self.connection_types = list(self._raw_config["connection_types"].keys())
        self.connection_type_weights = [
            self._raw_config["connection_types"][c]["weight"]
            for c in self.connection_types
        ]

        # ── Regions and Towers ──
        # We pre-build a flat list of all towers with their region.
        # This makes it easy to pick a random tower later.
        #
        # Example result:
        # [
        #     {"tower_id": "MAD-C-001", "region": "madrid_central"},
        #     {"tower_id": "MAD-C-002", "region": "madrid_central"},
        #     ...
        #     {"tower_id": "RUR-N-005", "region": "rural_north"},
        # ]
        self.towers = []
        for region_name, region_config in self._raw_config["regions"].items():
            prefix = region_config["tower_prefix"]
            count = region_config["tower_count"]

            for i in range(1, count + 1):
                self.towers.append({
                    "tower_id": f"{prefix}-{i:03d}",
                    "region": region_name,
                })

        # ── Error Codes ──
        # We need to pick error codes based on event type, so we 
        # pre-build a lookup: event_type → [list of applicable error codes]
        #
        # Example result:
        # {
        #     "VOICE_CALL": {
        #         "codes": ["E-1001", "E-1002", "E-1003", ...],
        #         "weights": [0.30, 0.20, 0.10, ...],
        #         "severities": ["MEDIUM", "HIGH", "CRITICAL", ...]
        #     },
        #     ...
        # }
        self.error_codes_by_event_type = {}

        for event_type in self.event_types:
            codes = []
            weights = []
            severities = []

            for code, code_config in self._raw_config["error_codes"].items():
                if event_type in code_config["applicable_to"]:
                    codes.append(code)
                    weights.append(code_config["weight"])
                    severities.append(code_config["severity"])

            # Normalize weights so they sum to 1.0
            # Why? random.choices requires weights, and if we filter
            # out some error codes (because they don't apply to this
            # event type), the remaining weights might not sum to 1.0.
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights] if total_weight > 0 else weights

            self.error_codes_by_event_type[event_type] = {
                "codes": codes,
                "weights": normalized_weights,
                "severities": severities,
            }

        # ── Duration Ranges ──
        self.duration_ranges = self._raw_config["duration_ms_ranges"]

    # ── Public Interface ──────────────────────────────────────────────

    def get_duration_range(self, event_type: str) -> dict:
        """Returns {"min": ..., "max": ...} for the given event type."""
        return self.duration_ranges[event_type]

    def get_error_info(self, event_type: str) -> dict:
        """Returns applicable error codes, weights, and severities for an event type."""
        return self.error_codes_by_event_type[event_type]

    def __repr__(self) -> str:
        """
        Makes the object print useful info when you do print(config).
        Helpful for debugging.
        """
        return (
            f"ConfigLoader("
            f"event_types={len(self.event_types)}, "
            f"towers={len(self.towers)}, "
            f"error_codes={len(self._raw_config['error_codes'])})"
        )