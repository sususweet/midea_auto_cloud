"""T0x45 screen-switch / smart panel gateway mapping.

COLMO smart panel gateways (e.g. CGZKS1, category screen-switch) report as
T0x45. Official Lua (T_0000_45_40100001_*) is a stub — dataToJson/jsonToData
are empty — so status/lua/get always fails and used to mark the device
unavailable after 3 polls (issue #271). Keep queries empty; the coordinator
polls /v1/super-gateway/panel/switch/query instead.

Control entities stay empty until live panel/curtain attribute keys are known.
"""

_EMPTY = {
    "rationale": ["off", "on"],
    # Do not hit status/lua/get — Lua codec is a no-op for this type.
    "queries": [],
    "centralized": [],
    "entities": {},
}

DEVICE_MAPPING = {
    "default": dict(_EMPTY),
    "default_screen_switch": dict(_EMPTY),
    # Observed on COLMO CGZKS1-style panel (sn8 40100001, plugin T0x45_10006371)
    "40100001": dict(_EMPTY),
}
