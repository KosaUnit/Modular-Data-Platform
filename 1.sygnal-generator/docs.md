# Telecom Network Event Pipeline — Data Documentation

## Data Dictionary

+-------------------+------------------------------------+------------------------------------------------+
| Field             | Why It Exists                      | What You'll Do With It                         |
+-------------------+------------------------------------+------------------------------------------------+
| event_id          | Unique identifier for each event   | Deduplication (detect duplicate messages)      |
| timestamp         | When the event happened            | Time windows, trend analysis, SLA calculation  |
| event_type        | Type of network interaction        | Group by type (e.g., voice vs data failures)   |
| status            | Whether it worked                  | Filter failures, compute failure rate          |
| tower_id          | Which cell tower                   | Identify problematic towers                    |
| region            | Geographic area                    | SLA compliance, regional dashboards            |
| duration_ms       | Connection duration                | Analyze drops, latency tracking                |
| error_code        | What went wrong (if failed)        | Root cause analysis via grouping               | 
| error_severity    | Severity of error                  | Filter alerts (HIGH/CRITICAL only)             |
| device_type       | Type of device                     | Analyze failures by device category            |
| connection_type   | Network type (3G/4G/5G)            | Compare reliability across technologies        |
+-------------------+------------------------------------+------------------------------------------------+

## Null Rules

When status = SUCCESS:
    error_code     → null
    error_severity → null

When status = FAILED / DROPPED / DEGRADED:
    error_code     → always populated
    error_severity → always populated (derived from error_code)

## Weights in config/event_schema.json

Weight = probability of that value being chosen.

"statuses": {
    "SUCCESS":  0.90   →  90% of events are successful
    "FAILED":   0.05   →   5% fail completely
    "DROPPED":  0.03   →   3% drop mid-connection
    "DEGRADED": 0.02   →   2% work but poorly
}                       
               Total: 1.00

This means if you generate 1000 events:
~900 will be SUCCESS
~50 will be FAILED
~30 will be DROPPED  
~20 will be DEGRADED

These numbers are roughly realistic for a healthy network.
When you simulate an INCIDENT, you'll temporarily change these weights
(e.g., FAILED jumps to 0.40 for a specific tower).


## Error Codes

+--------+-------------------------------+-----------+--------------------------------------+
| Code   | Description                   | Severity  | Analysis Story                       |
+--------+-------------------------------+-----------+--------------------------------------+
| E-1001 | Connection timeout            | MEDIUM    | Overloaded network?                  |
| E-1002 | Tower capacity exceeded       | HIGH      | Too many users on one tower          |
| E-1003 | Authentication failure        | CRITICAL  | Security issue or SIM problems       |
| E-2001 | Signal quality below threshold| LOW       | Weather? Obstruction? Tower damage?  |
| E-2002 | Handover failure              | HIGH      | Towers not coordinating properly     |
| E-3001 | Network routing error         | CRITICAL  | Core network problem, wide impact    |
| E-3002 | Hardware malfunction          | CRITICAL  | Specific tower equipment failing     |
+--------+-------------------------------+-----------+--------------------------------------+

## Error Code Applicability

Not every error code applies to every event type.

+--------+------------+------------+-----+-----------+
|        | VOICE_CALL | DATA_SESSION| SMS | HANDOVER |
+--------+------------+------------+-----+-----------+
| E-1001 |     ✓      |     ✓      |     |          |
| E-1002 |     ✓      |     ✓      |     |    ✓     |
| E-1003 |     ✓      |     ✓      |  ✓  |          |
| E-2001 |     ✓      |     ✓      |     |          |
| E-2002 |            |            |     |    ✓      |
| E-3001 |     ✓      |     ✓      |  ✓  |          |
| E-3002 |     ✓      |     ✓      |  ✓  |    ✓     |
+--------+------------+------------+-----+-----------+

The generator must respect this: a HANDOVER event should never get error E-1001.


## Duration Ranges (milliseconds)

+---------------+---------+-----------+---------------------------+
| Event Type    | Min     | Max       | In Human Terms            |
+---------------+---------+-----------+---------------------------+
| VOICE_CALL    | 5,000   | 600,000   | 5 seconds to 10 minutes   |
| DATA_SESSION  | 1,000   | 3,600,000 | 1 second to 1 hour        |
| SMS           | 100     | 2,000     | 0.1 to 2 seconds          |
| HANDOVER      | 50      | 5,000     | 50ms to 5 seconds         |
+---------------+---------+-----------+---------------------------+

When status = FAILED  → duration is SHORT (failed quickly)
When status = DROPPED → duration is ANY (lasted some time, then failed)
When status = SUCCESS → duration is within normal range


