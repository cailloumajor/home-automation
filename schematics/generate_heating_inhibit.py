"""Generate a standalone low-voltage watchdog and latched inhibition study."""
from pathlib import Path
from kicad_drawing import Drawing, line, rectangle, write_library_table


HERE = Path(__file__).resolve().parent
d = Drawing("heating_controller_inhibit_bench", "HeatingInhibit")
d.define("R", "R", [(1, "", -5.08, 0, 0), (2, "", 5.08, 0, 180)],
    rectangle(-2.54, 1.016, 2.54, -1.016))
d.define("C", "C", [(1, "", -5.08, 0, 0), (2, "", 5.08, 0, 180)],
    line(-0.635, -2.54, -0.635, 2.54) + line(0.635, -2.54, 0.635, 2.54))
d.define("Push", "S", [(1, "", -5.08, 0, 0), (2, "", 5.08, 0, 180)],
    line(-2.54, 0, 2.54, 2.54))
d.define("Conn7", "J", [(i+1, "", 7.62, -i*5.08, 180) for i in range(7)],
    rectangle(-2.54, 2.54, 5.08, -33.02))


def chip(name, ref, value, x, y, left, right):
    pins = [(pin, label, -22.86, 30.48-i*10.16, 0)
        for i, (pin, label, _) in enumerate(left)]
    pins += [(pin, label, 22.86, 30.48-i*10.16, 180)
        for i, (pin, label, _) in enumerate(right)]
    d.define(name, "U", pins, rectangle(-20.32, 35.56, 20.32, -40.64))
    d.symbol(name, ref, value, x, y, title_offset=43.18)
    for side, entries in ((-1, left), (1, right)):
        for i, (_, _, net) in enumerate(entries):
            yy = y-30.48+i*10.16
            pin_x = x+side*22.86
            if net is None:
                d.no_connect(pin_x, yy)
            else:
                label_x = pin_x + (-12.7 if side < 0 else 10.16)
                d.wire(pin_x, yy, label_x, yy)
                d.label(net, label_x, yy)


def passive(name, ref, value, x, y, left, right):
    d.symbol(name, ref, value, x, y)
    d.wire(x-20.32, y, x-5.08, y)
    d.label(left, x-20.32, y)
    d.wire(x+5.08, y, x+20.32, y)
    d.label(right, x+20.32, y)


d.text("WATCHDOG + LATCHED INHIBITION - USB / 3V3 ONLY - STUDY / NO MAINS", 20.32, 15.24, 2)
d.text("New ARM interface: incompatible with GPIO10 -> OE_N wiring of LED bench E. See companion document.",
    20.32, 22.86, 1.3)
d.text("TPS3828-33 is not a guaranteed reset before H2 supply falls below 3.0 V. Power supervision remains unqualified.",
    20.32, 30.48, 1.3)

chip("TPS3828", "U6", "TPS3828-33DBVR / adapter", 76.2, 85.09,
    [(5, "VDD", "+3V3"), (2, "GND", "GND_TBT"),
        (3, "MR_N", "MR_N"), (4, "WDI", "WDI")],
    [(1, "RESET_OD_N", "HEALTH_RAW_N")])

chip("HC14", "U5", "SN74HC14N / Schmitt", 208.28, 85.09,
    [(1, "1A", "HEALTH_RAW_N"), (3, "2A", "HEALTH_INV"),
        (5, "3A", "GND_TBT"), (9, "4A", "GND_TBT"),
        (11, "5A", "GND_TBT"), (13, "6A", "GND_TBT"), (7, "GND", "GND_TBT")],
    [(2, "1Y", "HEALTH_INV"), (4, "2Y", "HEALTH_N"),
        (6, "3Y", None), (8, "4Y", None), (10, "5Y", None),
        (12, "6Y", None), (14, "VCC", "+3V3")])

chip("HC74", "U3", "SN74HC74N / arm memory", 330.2, 85.09,
    [(1, "1CLR_N", "HEALTH_N"), (2, "1D", "+3V3"),
        (3, "1CLK", "ARM"), (4, "1PRE_N", "+3V3"),
        (10, "2PRE_N", "+3V3"), (11, "2CLK", "GND_TBT"), (12, "2D", "GND_TBT")],
    [(5, "1Q", "ARMED_Q"), (6, "1Q_N", None), (8, "2Q_N", None),
        (9, "2Q", None), (13, "2CLR_N", "GND_TBT"),
        (14, "VCC", "+3V3"), (7, "GND", "GND_TBT")])

chip("HC10", "U4", "SN74HC10N / output gate", 330.2, 208.28,
    [(1, "1A", "ARMED_Q"), (2, "1B", "ARM"), (13, "1C", "HEALTH_N"),
        (3, "2A", "GND_TBT"), (4, "2B", "GND_TBT"),
        (5, "2C", "GND_TBT"), (7, "GND", "GND_TBT")],
    [(12, "1Y", "OE_N"), (6, "2Y", None), (8, "3Y", None),
        (9, "3A", "GND_TBT"), (10, "3B", "GND_TBT"),
        (11, "3C", "GND_TBT"), (14, "VCC", "+3V3")])

passive("R", "R30", "4k7 / 1%", 76.2, 140.97, "+3V3", "HEALTH_RAW_N")
passive("R", "R31", "10k / 1%", 76.2, 158.75, "+3V3", "MR_N")
passive("R", "R32", "1k / 1%", 76.2, 234.95, "WDI", "GND_TBT")
passive("R", "R33", "10k / 1%", 76.2, 252.73, "ARM", "GND_TBT")
passive("R", "R34", "10k / 1%", 208.28, 234.95, "+3V3", "OE_N")
passive("Push", "SF1", "Hold = fault", 208.28, 252.73, "MR_N", "GND_TBT")

for ref, x, y, owner in (("C30", 175.26, 158.75, "U3"), ("C31", 241.3, 158.75, "U4"),
        ("C32", 175.26, 193.04, "U5"), ("C33", 241.3, 193.04, "U6")):
    passive("C", ref, f"100nF / near {owner}", x, y, "+3V3", "GND_TBT")

d.symbol("Conn7", "JINH1", "NEW INTERFACE / 1..7", 76.2, 180.34)
for i, net in enumerate(("+3V3", "GND_TBT", "ARM", "WDI", "ARMED_Q", "HEALTH_N", "OE_N")):
    yy = 180.34+i*5.08
    d.wire(83.82, yy, 104.14, yy)
    d.label(net, 104.14, yy)

d.text("HC14 uses two inverters: slow open-drain rise is cleaned before HC74 / HC10 inputs.", 20.32, 269.24, 1.2)
d.text("OE_N high inhibits both 595s. Keep one OE pull-up only. No direct GPIO10 -> OE_N or old S1 -> 3V3 wiring.",
    20.32, 276.86, 1.2)
d.save(HERE, "Heating controller - latched inhibition / LOW VOLTAGE STUDY", date="2026-11-01", revision="F-study")
write_library_table(HERE)
