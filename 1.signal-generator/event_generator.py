import random
import uuid
from datetime import datetime, timezone

from config_loader import ConfigLoader


class EventGenerator:
    """
    Creates individual telecom network events.
    """

    def __init__(self, config: ConfigLoader):
        """
        Args:
            config: A loaded ConfigLoader instance.
        """
        self.config = config

    def generate_event(self) -> dict:
        """
        Generates a single network event.
        
        Returns:
            A dictionary representing one network event, ready to be 
            serialized to JSON.
            
        How it works:
            1. Pick random event type (weighted)
            2. Pick random status (weighted)
            3. Pick random tower (which gives us the region)
            4. Pick random device and connection type (weighted)
            5. If status is not SUCCESS, assign an error code
            6. Calculate duration based on status and event type
            7. Package everything into a dictionary
        """
        # Step 1: What kind of event?
        event_type = self._pick_weighted(
            self.config.event_types,
            self.config.event_type_weights,
        )

        # Step 2: Did it succeed or fail?
        status = self._pick_weighted(
            self.config.statuses,
            self.config.status_weights,
        )

        # Step 3: Where did it happen?
        tower = random.choice(self.config.towers)

        # Step 4: What device and connection?
        device_type = self._pick_weighted(
            self.config.device_types,
            self.config.device_type_weights,
        )
        connection_type = self._pick_weighted(
            self.config.connection_types,
            self.config.connection_type_weights,
        )

        # Step 5: Error details (only if something went wrong)
        error_code, error_severity = self._get_error_details(
            event_type, status
        )

        # Step 6: How long did it last?
        duration_ms = self._calculate_duration(event_type, status)

        # Step 7: Build the event
        event = {
            "event_id": self._generate_event_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "status": status,
            "tower_id": tower["tower_id"],
            "region": tower["region"],
            "duration_ms": duration_ms,
            "error_code": error_code,
            "error_severity": error_severity,
            "device_type": device_type,
            "connection_type": connection_type,
        }

        return event

    # Private Helper Methods 

    def _pick_weighted(self, choices: list, weights: list) -> str:
        """
        Picks a random item from choices, using weights to determine probability.
        
        Example:
            choices = ["SUCCESS", "FAILED", "DROPPED", "DEGRADED"]
            weights = [0.90,      0.05,     0.03,      0.02]
            
            This will return "SUCCESS" ~90% of the time.
        
        random.choices returns a list (even for k=1), so we take [0].
        
        Why random.choices and not random.choice?
            random.choice  → equal probability for all items
            random.choices → supports weights (what we need)
        """
        return random.choices(choices, weights=weights, k=1)[0]

    def _generate_event_id(self) -> str:
        """
        Creates a unique event ID.
        
        Format: evt-<timestamp_ms>-<short_uuid>
        Example: evt-1705312981456-a8f2b3c1
        
        Why this format?
            - "evt-" prefix: makes it obvious this is an event ID in logs
            - timestamp: events sort chronologically by ID (useful for debugging)
            - short UUID: guarantees uniqueness even if two events have the same ms
            
        uuid4() generates a random UUID. We take the first 8 characters 
        because full UUIDs are long and we don't need that level of uniqueness 
        for a project.
        """
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        short_uuid = uuid.uuid4().hex[:8]
        return f"evt-{timestamp_ms}-{short_uuid}"

    def _get_error_details(
        self, event_type: str, status: str
    ) -> tuple[str | None, str | None]:
        """
        Determines error code and severity for an event.
        
        Logic:
            - SUCCESS events → no error (None, None)
            - Non-SUCCESS events → pick a random error code that applies to 
              this event type
              
        Returns:
            Tuple of (error_code, error_severity) or (None, None)
        """
        if status == "SUCCESS":
            return None, None

        error_info = self.config.get_error_info(event_type)

        # Edge case: if no error codes apply to this event type
        # (shouldn't happen with our config, but defensive coding)
        if not error_info["codes"]:
            return "E-9999", "UNKNOWN"

        # Pick a weighted random error code
        index = self._pick_weighted_index(
            error_info["weights"]
        )

        error_code = error_info["codes"][index]
        error_severity = error_info["severities"][index]

        return error_code, error_severity

    def _pick_weighted_index(self, weights: list) -> int:
        """
        Returns a random INDEX (not the value) based on weights.
        
        Why do we need the index instead of the value?
        Because we have parallel lists: codes, weights, severities.
        We need to pick the same index from all three lists to keep 
        them aligned.
        
        Example:
            codes      = ["E-1001", "E-1002", "E-1003"]
            weights    = [0.50,      0.30,     0.20]
            severities = ["MEDIUM",  "HIGH",   "CRITICAL"]
            
            If we pick index 1 → code="E-1002", severity="HIGH" ✓
        """
        indices = list(range(len(weights)))
        return random.choices(indices, weights=weights, k=1)[0]

    def _calculate_duration(self, event_type: str, status: str) -> int:
        """
        Calculates how long the event lasted in milliseconds.
        
        The key insight: the duration should be REALISTIC for the status.
        
        - SUCCESS:  full range (a successful call can be short or long)
        - FAILED:   very short (it failed quickly — couldn't connect)
        - DROPPED:  medium (it connected, ran for a while, then dropped)
        - DEGRADED: full range (it completed, just poorly)
        
        Why does this matter?
        In your Spark analysis, you might compute "average duration of 
        dropped calls." If dropped calls have realistic durations (10-60 
        seconds), you can make meaningful statements like "calls typically 
        drop after 30 seconds, suggesting a timeout configuration issue."
        """
        duration_range = self.config.get_duration_range(event_type)
        min_ms = duration_range["min"]
        max_ms = duration_range["max"]

        if status == "FAILED":
            # Failed events are short — the connection never established
            # or failed almost immediately.
            # Use 1% to 10% of the max duration.
            return random.randint(min_ms, max(min_ms, int(max_ms * 0.10)))

        elif status == "DROPPED":
            # Dropped events lasted a while before failing.
            # Use 10% to 60% of the max duration.
            lower = max(min_ms, int(max_ms * 0.10))
            upper = max(min_ms, int(max_ms * 0.60))
            return random.randint(lower, upper)

        else:
            # SUCCESS and DEGRADED — full range
            return random.randint(min_ms, max_ms)