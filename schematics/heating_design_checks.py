"""Reproducible V0.3 design calculations and ideal inhibition model.

No hardware access. Values are design assumptions, not measured currents.
This model does not verify analogue thresholds, propagation or PCB safety.
"""
from dataclasses import dataclass
from math import sqrt


def fault_resistor(voltage_rms, peak_current_limit):
    """Conservative peak limit, without credit for semiconductor resistance."""
    return sqrt(2) * voltage_rms / peak_current_limit


def allowed_resistor(normal_current, allowed_drop):
    return allowed_drop / normal_current


def resistor_interval(voltage_rms, peak_current_limit, normal_current,
                        allowed_drop, tolerance=0.01):
    # Lower actual R must limit the fault; upper actual R must limit the drop.
    low = fault_resistor(voltage_rms, peak_current_limit) / (1-tolerance)
    high = allowed_resistor(normal_current, allowed_drop) / (1+tolerance)
    return low, high


def led_current_bounds(v_min=4.75, v_max=5.25, vf_max=1.5,
                        vce_max=0.25, resistance=560, tolerance=0.01):
    return ((v_min-vf_max-vce_max)/(resistance*(1+tolerance)),
            v_max/(resistance*(1-tolerance)))


def watchdog_wdi_budget(resistance=1000, tolerance=0.01,
                        input_current=190e-6, supply_max=3.6):
    """Resistive budget using an assumed bound on absolute WDI input current.

    Does not qualify the GPIO voltage under load or the supervisor at 3.3 V.
    """
    low_voltage = input_current * resistance * (1+tolerance)
    high_current = supply_max / (resistance * (1-tolerance)) + input_current
    return low_voltage, high_current


@dataclass
class InhibitModel:
    """Ideal 1G74 D=1 / PRE=1 / CLK=ARM / CLR=HEALTH_N + NAND3.

    HEALTH_N is high only when both rails and the watchdog report healthy.
    An actual implementation must meet power-up and recovery/removal timing.
    """
    armed_memory: bool = False
    previous_arm: bool = False

    def step(self, arm, health_n):
        if not health_n:
            self.armed_memory = False
        elif arm and not self.previous_arm:
            self.armed_memory = True
        self.previous_arm = arm
        return not (arm and health_n and self.armed_memory)  # OE_N: high=inhibit


def zone_bits(mode_signals):
    """Map living/bath/bed1/bed2/bed3/corridor logical envelopes to 16 bits.

    FP1/FP2/FP3 share the living envelope, including its cycle phase.
    Bit 2*n is positive, bit 2*n+1 negative, with n starting at zero.
    """
    if len(mode_signals) != 6:
        raise ValueError("Expected six logical zones")
    physical_to_logical = (0, 0, 0, 5, 1, 2, 3, 4)
    word = 0
    for physical, logical in enumerate(physical_to_logical):
        positive, negative = mode_signals[logical]
        word |= int(bool(positive)) << (2*physical)
        word |= int(bool(negative)) << (2*physical+1)
    return word


def report():
    print("Assumptions only: 253 V RMS, 10 V allowed drop, resistors +/-1%")
    print("I_normal_mA,I_fault_peak_mA,R_nom_min_ohm,R_nom_max_ohm,interval_exists")
    for normal in (0.0001, 0.0005, 0.001, 0.005):
        for limit in (0.090, 0.036):
            low, high = resistor_interval(253, limit, normal, 10)
            print(f"{normal*1000:.1f},{limit*1000:.0f},{low:.1f},{high:.1f},{low <= high}")
    low, high = led_current_bounds()
    print(f"LED current envelope: {low*1000:.2f}..{high*1000:.2f} mA")
    print(f"16 LED current budget: {16*high*1000:.1f} mA")
    print(f"Worst-case 560 ohm resistor power: {5.25**2/(560*0.99)*1000:.1f} mW")


if __name__ == "__main__":
    report()
