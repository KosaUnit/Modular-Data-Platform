"""
It generates events at a configurable rate and prints them to console.
Later replace print with Kafka producer.
"""

import json
import time
import signal
import sys
from datetime import datetime, timezone

from config_loader import ConfigLoader
from event_generator import EventGenerator


# Configuration 
CONFIG_PATH = "config/event_schema.json"
EVENTS_PER_SECOND = 10  # Start slow. You can increase this later.


# Graceful Shutdown
running = True  # This flag controls the main loop

def shutdown_handler(signum, frame):
    """Called when Ctrl+C is pressed. Sets the flag to stop the loop."""
    global running
    print("\nShutdown signal received. Stopping generator...")
    running = False

def main():
    """
    Main loop that generates events at a configured rate.
    """
    # Setup 
    print("=" * 60)
    print("Telecom Network Event Generator")
    print("=" * 60)

    print(f"\nLoading config from: {CONFIG_PATH}")
    config = ConfigLoader(CONFIG_PATH)
    print(f"{config}")  # Prints: ConfigLoader(event_types=4, towers=58, error_codes=7)

    generator = EventGenerator(config)

    sleep_time = 1.0 / EVENTS_PER_SECOND
    print(f"\nGenerating {EVENTS_PER_SECOND} events/second")
    print(f"   (sleep between events: {sleep_time:.3f}s)")
    print(f"\n   Press Ctrl+C to stop.\n")
    print("-" * 60)

    # Counters for summary 
    total_events = 0
    status_counts = {}
    start_time = time.time()

    # Main Loop 
    while running:
        event = generator.generate_event()

        # Print the event as formatted JSON
        # indent=None would print on one line — but while developing,
        # we want to SEE the structure clearly. We'll switch to compact
        # format when sending to Kafka.
        print(json.dumps(event, indent=2))
        print()  # blank line between events for readability

        # Update counters
        total_events += 1
        status = event["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

        # Every 100 events, print a progress update
        # This confirm the generator is running 
        if total_events % 100 == 0:
            elapsed = time.time() - start_time
            actual_rate = total_events / elapsed if elapsed > 0 else 0
            print(f"{'─' * 60}")
            print(f"Progress: {total_events} events | "
                  f"Rate: {actual_rate:.1f} evt/s | "
                  f"Elapsed: {elapsed:.1f}s")
            print(f"   Status breakdown: {dict(status_counts)}")
            print(f"{'─' * 60}\n")

        time.sleep(sleep_time)

    # ── Summary (after Ctrl+C) ──
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("Generator Summary")
    print("=" * 60)
    print(f"   Total events generated: {total_events}")
    print(f"   Total time:             {elapsed:.1f}s")
    if elapsed > 0:
        print(f"   Average rate:           {total_events / elapsed:.1f} events/sec")
    print(f"\n   Status breakdown:")
    for status, count in sorted(status_counts.items()):
        percentage = (count / total_events * 100) if total_events > 0 else 0
        print(f"      {status:10s}: {count:6d} ({percentage:5.1f}%)")
    print("=" * 60)


# ── Entry Point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    main()