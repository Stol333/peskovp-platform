from __future__ import annotations

import sys
from pathlib import Path

API_SRC = Path(__file__).resolve().parents[1] / "src"
VPN_ROUTING_SRC = Path(__file__).resolve().parents[3] / "packages" / "vpn-routing" / "src"

if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))
if str(VPN_ROUTING_SRC) not in sys.path:
    sys.path.insert(0, str(VPN_ROUTING_SRC))

