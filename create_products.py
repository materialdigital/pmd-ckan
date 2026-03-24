#!/usr/bin/env python3
"""
Create 10 dummy industrial product datasets via the CKAN API.

Usage:
    CKAN_URL=https://docker-dev.iwm.fraunhofer.de \
    CKAN_API_KEY=<your-api-key> \
    python fixtures/create_products.py

The script is idempotent: it skips products that already exist.
"""

import os
import sys
import json
import requests

CKAN_URL = (
    os.environ.get("CKAN_URL")
    or os.environ.get("CKAN_SITE_URL")
    or "http://localhost:5000"
).rstrip("/")

CKAN_API_KEY = (
    os.environ.get("CKAN_API_KEY")
    or os.environ.get("BACKGROUNDJOBS_API_TOKEN")
    or ""
)

SSL_VERIFY = os.environ.get("SSL_VERIFY", "True").lower() not in ("false", "0", "no")

if not CKAN_API_KEY:
    print("ERROR: Set CKAN_API_KEY or BACKGROUNDJOBS_API_TOKEN environment variable.", file=sys.stderr)
    sys.exit(1)

# CKAN accepts both X-CKAN-API-Key and Authorization headers
HEADERS = {"Authorization": CKAN_API_KEY, "Content-Type": "application/json"}

ORG_NAME = "demo-manufacturer"
ORG_TITLE = "Demo Manufacturer GmbH"


def api(endpoint, payload):
    url = f"{CKAN_URL}/api/3/action/{endpoint}"
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=30, verify=SSL_VERIFY)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"{endpoint} failed: {data.get('error')}")
    return data["result"]


def api_get(endpoint, params):
    url = f"{CKAN_URL}/api/3/action/{endpoint}"
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30, verify=SSL_VERIFY)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"{endpoint} failed: {data.get('error')}")
    return data["result"]


def upload_text_resource(pkg_name, name, description, fmt, content, mimetype):
    """Upload an in-memory text file as a CKAN resource."""
    url = f"{CKAN_URL}/api/3/action/resource_create"
    files = {
        "upload": (f"{name.lower().replace(' ', '_')}.{fmt.lower()}", content.encode(), mimetype),
    }
    data = {
        "package_id": pkg_name,
        "name": name,
        "description": description,
        "format": fmt,
    }
    resp = requests.post(
        url,
        headers={"Authorization": CKAN_API_KEY},
        data=data,
        files=files,
        timeout=30,
        verify=SSL_VERIFY,
    )
    result = resp.json()
    if not result.get("success"):
        raise RuntimeError(f"resource_create failed: {result.get('error')}")
    return result["result"]


def add_link_resource(pkg_name, name, description, resource_url, fmt):
    return api("resource_create", {
        "package_id": pkg_name,
        "name": name,
        "description": description,
        "url": resource_url,
        "format": fmt,
    })


def ensure_org():
    try:
        return api_get("organization_show", {"id": ORG_NAME})
    except RuntimeError:
        return api("organization_create", {
            "name": ORG_NAME,
            "title": ORG_TITLE,
            "description": (
                "A demo manufacturer providing industrial components and assemblies. "
                "All product data is for demonstration purposes only."
            ),
        })


def create_or_skip(pkg_def):
    try:
        existing = api_get("package_show", {"id": pkg_def["name"]})
        print(f"  [skip] '{pkg_def['name']}' already exists.")
        return None
    except RuntimeError:
        return api("package_create", pkg_def)


# ---------------------------------------------------------------------------
# Product definitions
# ---------------------------------------------------------------------------

PRODUCTS = [

    # 1 ----------------------------------------------------------------
    {
        "name": "industrial-bolt-m8-class-109",
        "title": "Industrial Bolt M8 Class 10.9",
        "notes": (
            "High-strength metric hexagon head bolt M8 × 50 mm, property class 10.9. "
            "Manufactured to DIN EN ISO 4014. Suitable for structural steel connections, "
            "machinery and automotive applications. Zinc-nickel plated for corrosion resistance."
        ),
        "tags": [{"name": "fasteners"}, {"name": "bolts"}, {"name": "hardware"}, {"name": "steel"}],
        "extras": [
            {"key": "product_number", "value": "BOLT-M8-109-50"},
            {"key": "standard", "value": "DIN EN ISO 4014"},
            {"key": "material_class", "value": "Steel 10.9"},
        ],
        "resources": {
            "datasheet_md": (
                "# Industrial Bolt M8 Class 10.9\n\n"
                "## Overview\nHigh-strength hex head bolt for structural and mechanical assemblies.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Thread | M8 |\n| Length | 50 mm |\n| Property Class | 10.9 |\n"
                "| Head Type | Hexagon (DIN EN ISO 4014) |\n| Surface | Zinc-nickel plated |\n"
                "| Tensile Strength | 1040 N/mm² |\n| Yield Strength | 940 N/mm² |\n"
                "| Proof Load | 830 N/mm² |\n| Hardness | 33–39 HRC |\n\n"
                "## Safety Instructions\n\n"
                "- Do not exceed the specified tightening torque (25 Nm for M8).\n"
                "- Inspect for thread damage before use.\n"
                "- Use appropriate PPE when handling sharp-edged fasteners.\n"
                "- Do not use if corrosion or deformation is visible.\n\n"
                "## Handling & Storage\n\n"
                "Store in a dry location below 40 °C. Keep away from moisture and corrosive agents. "
                "Sort and store in labelled containers to prevent mix-up with lower-grade fasteners.\n\n"
                "## Regulatory Compliance\n\nCE marked. RoHS compliant. REACH compliant.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Thread diameter,8,mm\n"
                "Length,50,mm\n"
                "Property class,10.9,-\n"
                "Tensile strength,1040,N/mm²\n"
                "Yield strength (0.2%),940,N/mm²\n"
                "Proof load stress,830,N/mm²\n"
                "Min. elongation after fracture,9,%\n"
                "Hardness (HRC),33–39,-\n"
                "Tightening torque (dry),25,Nm\n"
                "Tightening torque (lubricated),19,Nm\n"
                "Mass per piece,~8,g\n"
            ),
            "link_url": "https://www.iso.org/standard/67254.html",
            "link_name": "ISO 4014 Standard",
            "link_desc": "DIN EN ISO 4014 Hexagon head bolts — Product grades A and B",
        },
    },

    # 2 ----------------------------------------------------------------
    {
        "name": "o-ring-nbr-70-shore-as568-214",
        "title": "O-Ring NBR 70 Shore A — AS568-214",
        "notes": (
            "Standard O-ring in nitrile butadiene rubber (NBR), hardness 70 Shore A, "
            "inner diameter 37.47 mm, cross-section 3.53 mm (AS568-214). "
            "Suitable for static and dynamic hydraulic and pneumatic sealing applications "
            "in oil, fuel, and water media up to 120 °C."
        ),
        "tags": [{"name": "sealing"}, {"name": "o-ring"}, {"name": "rubber"}, {"name": "hydraulics"}],
        "extras": [
            {"key": "product_number", "value": "OR-NBR70-AS214"},
            {"key": "standard", "value": "AS568-214 / DIN 3771"},
            {"key": "material_class", "value": "NBR 70 Shore A"},
        ],
        "resources": {
            "datasheet_md": (
                "# O-Ring NBR 70 Shore A — AS568-214\n\n"
                "## Overview\nGeneral-purpose elastomeric O-ring for hydraulic and pneumatic sealing.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Material | NBR (Nitrile Butadiene Rubber) |\n| Hardness | 70 Shore A |\n"
                "| Inner Diameter (d1) | 37.47 mm |\n| Cross-section (d2) | 3.53 mm |\n"
                "| Colour | Black |\n| Temperature range | −30 °C to +120 °C |\n"
                "| Max. pressure (static) | 200 bar |\n| Max. pressure (dynamic) | 100 bar |\n\n"
                "## Media Compatibility\n\nCompatible with: mineral oils (HL, HLP), diesel fuel, water-glycol. "
                "Not suitable for: ketones, esters, aromatic hydrocarbons.\n\n"
                "## Safety Instructions\n\n"
                "- Do not use beyond rated temperature and pressure limits.\n"
                "- Check compatibility with process fluid before installation.\n"
                "- Replace O-ring at every reassembly; never reuse removed seals.\n"
                "- Wear gloves when handling to avoid contamination.\n\n"
                "## Handling & Storage\n\n"
                "Store in original packaging away from UV light, ozone, heat sources, and sharp objects. "
                "Shelf life: 7 years at ≤ 15 °C / ≤ 65 % RH (per ISO 2230).\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Material,NBR,-\n"
                "Hardness,70,Shore A\n"
                "Inner diameter d1,37.47,mm\n"
                "Cross-section d2,3.53,mm\n"
                "Temperature min,-30,°C\n"
                "Temperature max,120,°C\n"
                "Max static pressure,200,bar\n"
                "Max dynamic pressure,100,bar\n"
                "Elongation at break,>300,%\n"
                "Tensile strength,>10,MPa\n"
                "Compression set (22h/100°C),<25,%\n"
            ),
            "link_url": "https://www.iso.org/standard/32269.html",
            "link_name": "ISO 3601-1: O-ring Dimensions",
            "link_desc": "ISO 3601-1 Fluid power systems — O-rings — Part 1: Inside diameters, cross-sections, tolerances",
        },
    },

    # 3 ----------------------------------------------------------------
    {
        "name": "ball-bearing-6205-2rs",
        "title": "Deep Groove Ball Bearing 6205-2RS",
        "notes": (
            "Single-row deep groove ball bearing 6205-2RS1 with rubber seals on both sides. "
            "Bore 25 mm, outer diameter 52 mm, width 15 mm. Pre-greased for life. "
            "Suitable for electric motors, pumps, gearboxes, and general machinery."
        ),
        "tags": [{"name": "bearings"}, {"name": "rolling-elements"}, {"name": "mechanical"}],
        "extras": [
            {"key": "product_number", "value": "BRG-6205-2RS"},
            {"key": "standard", "value": "DIN 625-1 / ISO 15"},
            {"key": "material_class", "value": "Bearing steel 100Cr6"},
        ],
        "resources": {
            "datasheet_md": (
                "# Deep Groove Ball Bearing 6205-2RS\n\n"
                "## Overview\nSingle-row deep groove ball bearing, sealed on both sides, pre-lubricated.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Designation | 6205-2RS1 |\n| Bore (d) | 25 mm |\n"
                "| Outer diameter (D) | 52 mm |\n| Width (B) | 15 mm |\n"
                "| Dynamic load rating (C) | 14.0 kN |\n| Static load rating (C0) | 7.8 kN |\n"
                "| Limiting speed (grease) | 13 000 rpm |\n| Fatigue limit load | 0.34 kN |\n"
                "| Mass | 120 g |\n| Lubrication | Grease — long-life lithium |\n\n"
                "## Safety Instructions\n\n"
                "- Do not exceed the rated dynamic or static load.\n"
                "- Use correct tools (press or induction heater) for installation; "
                "  never strike the bearing races.\n"
                "- Ensure shaft and housing tolerances per ISO 286 recommendation.\n"
                "- PPE required: safety glasses during pressing operations.\n\n"
                "## Handling & Storage\n\n"
                "Store in original packaging in a clean, dry environment (< 60 % RH). "
                "Do not expose to vibration during storage. Shelf life: 3 years.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Bore diameter d,25,mm\n"
                "Outer diameter D,52,mm\n"
                "Width B,15,mm\n"
                "Dynamic load rating C,14.0,kN\n"
                "Static load rating C0,7.8,kN\n"
                "Fatigue limit load Pu,0.34,kN\n"
                "Limiting speed (grease),13000,rpm\n"
                "Limiting speed (oil),17000,rpm\n"
                "Operating temperature min,-30,°C\n"
                "Operating temperature max,120,°C\n"
                "Mass,120,g\n"
            ),
            "link_url": "https://www.iso.org/standard/57617.html",
            "link_name": "ISO 15:2017 — Rolling bearings",
            "link_desc": "ISO 15:2017 Rolling bearings — Radial bearings — Boundary dimensions",
        },
    },

    # 4 ----------------------------------------------------------------
    {
        "name": "hydraulic-cylinder-double-acting-50mm",
        "title": "Hydraulic Cylinder Double-Acting Ø50 mm",
        "notes": (
            "Double-acting hydraulic cylinder with 50 mm bore, 100 mm stroke, "
            "rated to 250 bar working pressure. Steel body, chrome-plated piston rod. "
            "Port size G 3/8. Suitable for industrial presses, clamping, and lifting."
        ),
        "tags": [{"name": "hydraulics"}, {"name": "actuators"}, {"name": "cylinders"}],
        "extras": [
            {"key": "product_number", "value": "HYD-CYL-50-100"},
            {"key": "standard", "value": "ISO 6022"},
            {"key": "material_class", "value": "Steel / Chrome-plated rod"},
        ],
        "resources": {
            "datasheet_md": (
                "# Hydraulic Cylinder Double-Acting Ø50 mm\n\n"
                "## Overview\nCompact double-acting cylinder for industrial hydraulic circuits.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Bore diameter | 50 mm |\n| Stroke | 100 mm |\n"
                "| Rod diameter | 28 mm |\n| Working pressure | 250 bar |\n"
                "| Test pressure | 375 bar |\n| Push force @ 250 bar | ~49 kN |\n"
                "| Pull force @ 250 bar | ~34 kN |\n| Port size | G 3/8 |\n"
                "| Seals | Polyurethane / NBR |\n| Operating temperature | −20 °C to +80 °C |\n"
                "| Medium | Hydraulic oil HLP 32–100 |\n\n"
                "## Safety Instructions\n\n"
                "- **Pressure hazard**: Never work on the cylinder under pressure.\n"
                "- Depressurise the system completely before maintenance or disassembly.\n"
                "- Do not exceed maximum operating pressure. Use a calibrated pressure relief valve.\n"
                "- Avoid side loads greater than 10 % of axial load rating.\n"
                "- Wear face shield and protective clothing when working with high-pressure hydraulics.\n\n"
                "## Handling & Storage\n\n"
                "Cap all ports during storage. Store vertically or horizontally on support blocks. "
                "Protect the rod from scratches. Apply light oil to rod before storage.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Bore diameter,50,mm\n"
                "Stroke,100,mm\n"
                "Rod diameter,28,mm\n"
                "Working pressure,250,bar\n"
                "Test pressure,375,bar\n"
                "Push force,49,kN\n"
                "Pull force,34,kN\n"
                "Port size,G 3/8,-\n"
                "Operating temp min,-20,°C\n"
                "Operating temp max,80,°C\n"
                "Weight (approx.),3.2,kg\n"
            ),
            "link_url": "https://www.iso.org/standard/33467.html",
            "link_name": "ISO 6022 — Hydraulic cylinders",
            "link_desc": "ISO 6022 Hydraulic fluid power — Mounting dimensions for single rod cylinders",
        },
    },

    # 5 ----------------------------------------------------------------
    {
        "name": "plc-controller-compact-cpu-24v",
        "title": "Compact PLC Controller — CPU 24 V DC",
        "notes": (
            "Programmable logic controller with 14 digital inputs / 10 digital outputs, "
            "24 V DC supply, integrated Ethernet port. "
            "IEC 61131-3 compliant. DIN-rail mount. IP20 protection."
        ),
        "tags": [{"name": "automation"}, {"name": "plc"}, {"name": "electronics"}, {"name": "control"}],
        "extras": [
            {"key": "product_number", "value": "PLC-CPU-1214DC"},
            {"key": "standard", "value": "IEC 61131-3 / UL 508"},
            {"key": "material_class", "value": "Electronics / Plastics enclosure"},
        ],
        "resources": {
            "datasheet_md": (
                "# Compact PLC Controller — CPU 24 V DC\n\n"
                "## Overview\nCompact DIN-rail PLC for machine automation and process control.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Supply voltage | 24 V DC |\n| Digital inputs | 14 |\n"
                "| Digital outputs | 10 (transistor, sourcing) |\n"
                "| Analogue inputs | 2 |\n| Work memory | 100 kB |\n"
                "| Communication | Ethernet (PROFINET) |\n"
                "| Programming languages | LAD, FBD, STL, SCL, GRAPH |\n"
                "| Protection class | IP20 |\n| Mounting | 35 mm DIN rail |\n"
                "| Operating temperature | 0 °C to 55 °C |\n"
                "| Dimensions (W×H×D) | 110 × 100 × 75 mm |\n\n"
                "## Safety Instructions\n\n"
                "- **Electrical hazard**: Disconnect mains supply before installation or wiring.\n"
                "- Observe polarity when connecting 24 V DC supply.\n"
                "- Do not modify the device housing or internal circuitry.\n"
                "- Install in a suitable IP54+ enclosure if the environment requires it.\n"
                "- Comply with local electrical codes and EMC regulations.\n\n"
                "## Handling & Storage\n\n"
                "Store in original packaging, dry, 0–60 °C, max. 95 % RH non-condensing. "
                "Discharge static electricity (ESD) before handling the PCB.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Supply voltage,24,V DC\n"
                "Digital inputs,14,-\n"
                "Digital outputs,10,-\n"
                "Analogue inputs,2,-\n"
                "Analogue outputs,0,-\n"
                "Work memory,100,kB\n"
                "Load memory (onboard),1,MB\n"
                "Cycle time (bit instructions),0.08,µs\n"
                "Ethernet ports,1,-\n"
                "IP protection class,IP20,-\n"
                "Operating temp min,0,°C\n"
                "Operating temp max,55,°C\n"
                "Width,110,mm\n"
                "Height,100,mm\n"
                "Depth,75,mm\n"
                "Weight,430,g\n"
            ),
            "link_url": "https://en.wikipedia.org/wiki/Programmable_logic_controller",
            "link_name": "Wikipedia: Programmable Logic Controller",
            "link_desc": "Overview article on PLC technology and applications",
        },
    },

    # 6 ----------------------------------------------------------------
    {
        "name": "pneumatic-valve-5-2-way-g14",
        "title": "Pneumatic Directional Control Valve 5/2-Way G1/4",
        "notes": (
            "5/2-way single-solenoid pneumatic directional control valve, "
            "G1/4 port, 24 V DC coil, spring return. Flow rate 420 l/min (Kv 0.6). "
            "For controlling double-acting pneumatic cylinders."
        ),
        "tags": [{"name": "pneumatics"}, {"name": "valves"}, {"name": "automation"}],
        "extras": [
            {"key": "product_number", "value": "PNV-52-G14-24V"},
            {"key": "standard", "value": "ISO 5599-1"},
            {"key": "material_class", "value": "Aluminium body / Stainless steel spool"},
        ],
        "resources": {
            "datasheet_md": (
                "# Pneumatic Directional Control Valve 5/2-Way G1/4\n\n"
                "## Overview\nSingle-solenoid, spring-return 5/2-way valve for pneumatic cylinder control.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Valve type | 5/2-way, single solenoid, spring return |\n"
                "| Port size | G1/4 |\n| Supply voltage | 24 V DC |\n"
                "| Power consumption | 3.0 W |\n| Flow rate (at Δp = 6 bar) | 420 Nl/min |\n"
                "| Kv value | 0.6 m³/h |\n"
                "| Working pressure range | 2–10 bar |\n"
                "| Switching time (energise) | < 30 ms |\n"
                "| Switching time (de-energise) | < 40 ms |\n"
                "| IP protection | IP65 |\n"
                "| Operating temperature | −10 °C to +60 °C |\n"
                "| Lubrication | Oil-free or lightly lubricated air |\n\n"
                "## Safety Instructions\n\n"
                "- **Pressure hazard**: Vent the pneumatic system before working on the valve.\n"
                "- **Electrical hazard**: Disconnect power before wiring or removal.\n"
                "- Maximum supply pressure must not exceed 10 bar.\n"
                "- Use dry, filtered air (ISO 8573-1, Class 3). Particle size < 40 µm.\n"
                "- In dusty environments, add a suitable pre-filter.\n\n"
                "## Handling & Storage\n\nStore at 15–35 °C, max. 75 % RH. "
                "Cap ports to prevent contamination. Avoid shock and vibration.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Valve function,5/2-way spring return,-\n"
                "Port size,G1/4,-\n"
                "Coil voltage,24,V DC\n"
                "Power consumption,3.0,W\n"
                "Flow rate,420,Nl/min\n"
                "Kv value,0.6,m³/h\n"
                "Min working pressure,2,bar\n"
                "Max working pressure,10,bar\n"
                "Switching time (on),<30,ms\n"
                "Switching time (off),<40,ms\n"
                "IP protection,IP65,-\n"
                "Operating temp min,-10,°C\n"
                "Operating temp max,60,°C\n"
                "Weight,320,g\n"
            ),
            "link_url": "https://www.iso.org/standard/50828.html",
            "link_name": "ISO 5599-1 — Pneumatic valves",
            "link_desc": "ISO 5599-1 Pneumatic fluid power — 5-port directional control valves",
        },
    },

    # 7 ----------------------------------------------------------------
    {
        "name": "safety-relay-module-24vdc-2-no",
        "title": "Safety Relay Module 24 V DC — 2 N/O",
        "notes": (
            "Safety relay module for emergency-stop, light curtain, and door switch monitoring. "
            "24 V DC, 2 safety output contacts (N/O), manual / automatic reset, "
            "response time < 20 ms. Suitable for SIL 3 / PLe category 4 safety functions."
        ),
        "tags": [{"name": "safety"}, {"name": "relay"}, {"name": "emergency-stop"}, {"name": "sil3"}],
        "extras": [
            {"key": "product_number", "value": "SRM-24VDC-2NO"},
            {"key": "standard", "value": "IEC 62061 SIL 3 / ISO 13849-1 PLe Cat.4"},
            {"key": "material_class", "value": "Electronics"},
        ],
        "resources": {
            "datasheet_md": (
                "# Safety Relay Module 24 V DC — 2 N/O\n\n"
                "## Overview\nSafety relay for monitoring emergency-stop buttons, "
                "safety doors, and light curtains.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Supply voltage | 24 V DC |\n| Safety outputs | 2 × N/O |\n"
                "| Output contact rating | 6 A / 250 V AC, 6 A / 24 V DC |\n"
                "| Response time | < 20 ms |\n| Reset mode | Manual / automatic |\n"
                "| Safety level | SIL 3 (IEC 62061) / PLe Cat. 4 (ISO 13849-1) |\n"
                "| PFHD | 1.0 × 10⁻⁹ 1/h |\n| IP protection | IP40 |\n"
                "| Mounting | 35 mm DIN rail |\n"
                "| Operating temperature | 0 °C to 55 °C |\n\n"
                "## Safety Instructions\n\n"
                "- **Only qualified personnel** must install, wire, and commission this device.\n"
                "- Comply with IEC 60204-1 and local electrical safety standards.\n"
                "- The safety function must be validated after installation "
                "  (proof-test per ISO 13849-2).\n"
                "- Do not bypass or defeat safety contacts under any circumstances.\n"
                "- Perform a functional test of the entire safety circuit after any modification.\n\n"
                "## Handling & Storage\nStore in dry conditions, 0–60 °C, < 95 % RH non-condensing. "
                "Protect from ESD during handling.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Supply voltage,24,V DC\n"
                "Max supply voltage,30,V DC\n"
                "Safety outputs (N/O),2,-\n"
                "Output contact current,6,A\n"
                "Output contact voltage (AC),250,V AC\n"
                "Output contact voltage (DC),24,V DC\n"
                "Response time,<20,ms\n"
                "Safety integrity level,SIL 3,-\n"
                "Performance level,PLe Cat.4,-\n"
                "PFHD,1.0E-9,1/h\n"
                "Mission time,20,years\n"
                "IP protection,IP40,-\n"
                "Operating temp min,0,°C\n"
                "Operating temp max,55,°C\n"
                "Weight,150,g\n"
            ),
            "link_url": "https://en.wikipedia.org/wiki/Safety_integrity_level",
            "link_name": "Wikipedia: Safety Integrity Level",
            "link_desc": "Overview of Safety Integrity Levels (SIL) as defined in IEC 61508",
        },
    },

    # 8 ----------------------------------------------------------------
    {
        "name": "external-gear-pump-10cc-rev",
        "title": "External Gear Pump — 10 cc/rev",
        "notes": (
            "Fixed-displacement external gear pump, displacement 10 cc/rev, "
            "max. 250 bar continuous, max. speed 3500 rpm. "
            "SAE B-2 bolt flange, SAE A shaft. For mobile and industrial hydraulic power units."
        ),
        "tags": [{"name": "hydraulics"}, {"name": "pumps"}, {"name": "fluid-power"}],
        "extras": [
            {"key": "product_number", "value": "GP-EXT-10CC"},
            {"key": "standard", "value": "SAE J517 / ISO 3019-2"},
            {"key": "material_class", "value": "Cast iron / Steel gears"},
        ],
        "resources": {
            "datasheet_md": (
                "# External Gear Pump — 10 cc/rev\n\n"
                "## Overview\nFixed-displacement gear pump for industrial and mobile hydraulics.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Displacement | 10 cc/rev |\n| Max. continuous pressure | 250 bar |\n"
                "| Peak pressure (< 1 s) | 280 bar |\n| Max. speed | 3500 rpm |\n"
                "| Min. speed | 600 rpm |\n| Flow at 1500 rpm | ~14.8 l/min |\n"
                "| Inlet pressure range | −0.3 to +3 bar |\n"
                "| Operating temperature | −20 °C to +90 °C |\n"
                "| Viscosity range | 10–300 cSt |\n| Flange | SAE B-2 bolt |\n"
                "| Shaft | SAE A (splined 9T) |\n"
                "| Mass | 3.5 kg |\n\n"
                "## Safety Instructions\n\n"
                "- **Pressure hazard**: Fully depressurise before servicing.\n"
                "- Never run the pump dry — always prime before start-up.\n"
                "- Use a pressure relief valve to protect the pump from overpressure.\n"
                "- Ensure correct shaft coupling alignment (max. 0.05 mm TIR).\n"
                "- Use hydraulic oil with correct viscosity and cleanliness (ISO 4406 Class 17/15/12).\n\n"
                "## Handling & Storage\nFill ports with clean oil and cap before storage. "
                "Store in dry conditions. Rotate shaft monthly if stored > 3 months.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Displacement,10,cc/rev\n"
                "Max continuous pressure,250,bar\n"
                "Peak pressure,280,bar\n"
                "Max speed,3500,rpm\n"
                "Min speed,600,rpm\n"
                "Theoretical flow at 1500 rpm,15.0,l/min\n"
                "Volumetric efficiency at 250 bar,>90,%\n"
                "Inlet pressure min,-0.3,bar\n"
                "Inlet pressure max,3,bar\n"
                "Operating temp min,-20,°C\n"
                "Operating temp max,90,°C\n"
                "Viscosity min,10,cSt\n"
                "Viscosity max,300,cSt\n"
                "Mass,3.5,kg\n"
            ),
            "link_url": "https://en.wikipedia.org/wiki/Gear_pump",
            "link_name": "Wikipedia: Gear Pump",
            "link_desc": "Technical overview of external and internal gear pump technology",
        },
    },

    # 9 ----------------------------------------------------------------
    {
        "name": "emergency-stop-pushbutton-40mm",
        "title": "Emergency Stop Push Button Ø40 mm — IEC 60947",
        "notes": (
            "Mushroom-head emergency stop push button, 40 mm Ø, "
            "latching with key release, 1 N/C contact block. "
            "IP65, red/yellow. Meets IEC 60947-5-5 for e-stop applications."
        ),
        "tags": [{"name": "safety"}, {"name": "controls"}, {"name": "emergency-stop"}, {"name": "pushbutton"}],
        "extras": [
            {"key": "product_number", "value": "ESTOP-40MM-KEY"},
            {"key": "standard", "value": "IEC 60947-5-5 / EN ISO 13850"},
            {"key": "material_class", "value": "Polycarbonate / Zinc die-cast head"},
        ],
        "resources": {
            "datasheet_md": (
                "# Emergency Stop Push Button Ø40 mm — IEC 60947\n\n"
                "## Overview\nMushroom-head latching e-stop for control panel and machine installation.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Actuator | Ø40 mm mushroom head, red |\n"
                "| Frame / Bezel | Yellow |\n| Latching | Twist-to-release |\n"
                "| Contact type | 1 N/C |\n| Rated voltage (Ue) | 240 V AC / 110 V DC |\n"
                "| Rated current (Ie) | 10 A (AC-15) |\n"
                "| Mechanical endurance | 1 × 10⁶ operations |\n"
                "| IP protection | IP65 (with seal gasket) |\n"
                "| Mounting hole | Ø22 mm |\n"
                "| Operating temperature | −25 °C to +70 °C |\n"
                "| Standards | IEC 60947-5-5, EN ISO 13850 |\n\n"
                "## Safety Instructions\n\n"
                "- Install in easily visible and accessible location per EN ISO 13850.\n"
                "- The e-stop function must be wired in series with the safety circuit "
                "  (hardwired, not via PLC output).\n"
                "- Verify operation after installation and after any maintenance.\n"
                "- Do not use as a power-on switch or for routine stop of machinery.\n"
                "- Replace if mechanically damaged or if contact resistance > 100 mΩ.\n\n"
                "## Handling & Storage\nStore in dry conditions, original packaging. "
                "Operating temperature: −25 °C to +70 °C.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Actuator diameter,40,mm\n"
                "Mounting hole,22,mm\n"
                "Contact type,1 N/C,-\n"
                "Rated voltage (Ue),240,V AC\n"
                "Rated current (Ie AC-15),10,A\n"
                "Short-circuit protection (fuse),10,A gL/gG\n"
                "Mechanical endurance,1000000,operations\n"
                "Electrical endurance (AC-15),100000,operations\n"
                "IP protection,IP65,-\n"
                "Operating temp min,-25,°C\n"
                "Operating temp max,70,°C\n"
                "Weight,120,g\n"
            ),
            "link_url": "https://en.wikipedia.org/wiki/Kill_switch",
            "link_name": "Wikipedia: Kill Switch / Emergency Stop",
            "link_desc": "Overview of emergency stop principles and standards",
        },
    },

    # 10 ---------------------------------------------------------------
    {
        "name": "cable-gland-pg16-stainless-steel",
        "title": "Cable Gland PG16 — Stainless Steel IP68",
        "notes": (
            "Stainless steel cable gland PG16 thread, "
            "clamping range 10–14 mm, IP68 rated (10 m / 168 h). "
            "Single-compression design with locknut. "
            "For EMC-screened and unscreened cables in industrial environments."
        ),
        "tags": [{"name": "enclosures"}, {"name": "cable-management"}, {"name": "ip68"}, {"name": "stainless-steel"}],
        "extras": [
            {"key": "product_number", "value": "CG-PG16-SS-IP68"},
            {"key": "standard", "value": "IEC 60529 IP68 / EN 50262"},
            {"key": "material_class", "value": "Stainless steel 316L / NBR seal"},
        ],
        "resources": {
            "datasheet_md": (
                "# Cable Gland PG16 — Stainless Steel IP68\n\n"
                "## Overview\nStainless steel EMC cable gland for harsh industrial environments.\n\n"
                "## Technical Specifications\n\n"
                "| Property | Value |\n|---|---|\n"
                "| Thread | PG16 |\n| Clamping range | 10–14 mm |\n"
                "| Material (body) | Stainless steel 316L |\n"
                "| Material (seal/O-ring) | NBR |\n"
                "| IP protection | IP68 (10 m / 168 h) |\n"
                "| IP protection (panel) | IP66/IP67 |\n"
                "| UL certification | UL listed |\n"
                "| Operating temperature | −40 °C to +100 °C |\n"
                "| Tightening torque (body) | 25 Nm |\n"
                "| Panel hole (metric) | Ø22 mm |\n\n"
                "## Safety Instructions\n\n"
                "- Do not exceed rated tightening torque to avoid cracking the seal.\n"
                "- Ensure cable diameter is within the clamping range to maintain IP rating.\n"
                "- Apply anti-seize compound if used in chloride-rich or marine environments.\n"
                "- After installation, perform an IP68 pressure test per IEC 60529 if required.\n\n"
                "## Handling & Storage\n\nStore in original packaging, dry and clean. "
                "Inspect O-ring for damage before installation. Replace damaged O-rings. "
                "Shelf life: unlimited in original packaging.\n\n"
                "## Regulatory Compliance\n\nRoHS compliant. REACH compliant. UL listed.\n"
            ),
            "specs_csv": (
                "Property,Value,Unit\n"
                "Thread,PG16,-\n"
                "Clamping range min,10,mm\n"
                "Clamping range max,14,mm\n"
                "Panel hole diameter,22,mm\n"
                "Body material,316L stainless steel,-\n"
                "Seal material,NBR,-\n"
                "IP protection (assembled),IP68,-\n"
                "IP protection (panel),IP66/IP67,-\n"
                "Max tightening torque,25,Nm\n"
                "Operating temp min,-40,°C\n"
                "Operating temp max,100,°C\n"
                "Weight,45,g\n"
            ),
            "link_url": "https://en.wikipedia.org/wiki/IP_code",
            "link_name": "Wikipedia: IP Code (Ingress Protection)",
            "link_desc": "Explanation of IP rating system as defined in IEC 60529",
        },
    },
]


def main():
    print(f"Connecting to CKAN at {CKAN_URL}")

    print(f"Ensuring organisation '{ORG_NAME}' exists...")
    org = ensure_org()
    print(f"  Organisation ID: {org['id']}")

    created = 0
    skipped = 0

    for product in PRODUCTS:
        print(f"\nProcessing: {product['title']}")

        resources_def = product.pop("resources")
        pkg_def = {**product, "owner_org": ORG_NAME}

        result = create_or_skip(pkg_def)
        if result is None:
            skipped += 1
            continue

        pkg_name = result["name"]
        print(f"  Created package: {pkg_name}")

        # Upload Markdown datasheet
        upload_text_resource(
            pkg_name=pkg_name,
            name="Product Datasheet",
            description="Product overview, technical specifications, safety instructions and handling information.",
            fmt="MD",
            content=resources_def["datasheet_md"],
            mimetype="text/markdown",
        )
        print("    + Uploaded: Product Datasheet (MD)")

        # Upload CSV specs
        upload_text_resource(
            pkg_name=pkg_name,
            name="Technical Specifications",
            description="Machine-readable technical specifications in CSV format.",
            fmt="CSV",
            content=resources_def["specs_csv"],
            mimetype="text/csv",
        )
        print("    + Uploaded: Technical Specifications (CSV)")

        # Add external link
        add_link_resource(
            pkg_name=pkg_name,
            name=resources_def["link_name"],
            description=resources_def["link_desc"],
            resource_url=resources_def["link_url"],
            fmt="HTML",
        )
        print(f"    + Linked: {resources_def['link_name']}")

        created += 1

    print(f"\nDone. Created: {created}, Skipped (already exist): {skipped}")


if __name__ == "__main__":
    main()
