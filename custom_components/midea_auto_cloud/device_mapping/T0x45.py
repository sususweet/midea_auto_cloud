"""T0x45 screen-switch / smart panel gateway mapping.

COLMO smart panel gateways (e.g. CGZKS1, category screen-switch) report as
T0x45. Without this module, setup logs
`Can't load mapping file for type T0x45` (issue #271) and the device-status
entity stays unavailable for further protocol analysis.

Control entities are intentionally empty until Lua/plugin attribute keys are
confirmed from a live device-status dump.
"""

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {},
    },
    "default_screen_switch": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {},
    },
    # Observed on COLMO CGZKS1-style panel (sn8 40100001)
    "40100001": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {},
    },
}
