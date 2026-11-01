"""Engineering model checks, without network or hardware access."""
import importlib.util
from itertools import product
from pathlib import Path
import sys
import unittest


path = Path(__file__).resolve().parents[1] / "schematics/heating_design_checks.py"
spec = importlib.util.spec_from_file_location("heating_design_checks", path)
design = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = design
spec.loader.exec_module(design)


class DesignChecks(unittest.TestCase):
    def test_fault_pulse_cannot_reenable_without_new_arm_edge(self):
        model = design.InhibitModel()
        self.assertTrue(model.step(False, False))
        self.assertTrue(model.step(False, True))
        self.assertFalse(model.step(True, True))
        self.assertTrue(model.step(True, False))
        for _ in range(10):
            self.assertTrue(model.step(True, True))
        self.assertTrue(model.step(False, True))
        self.assertFalse(model.step(True, True))

    def test_reset_is_dominant_even_on_arm_edge(self):
        model = design.InhibitModel()
        self.assertTrue(model.step(True, False))
        self.assertTrue(model.step(True, True))

    def test_disarm_always_inhibits(self):
        model = design.InhibitModel()
        self.assertFalse(model.step(True, True))
        self.assertTrue(model.step(False, True))

    def test_every_state_obeys_output_gate(self):
        for memory, previous, arm, health in product((False, True), repeat=4):
            model = design.InhibitModel(memory, previous)
            output_disabled = model.step(arm, health)
            if not health or not arm:
                self.assertTrue(output_disabled)

    def test_eight_outputs_and_living_phase_are_mapped(self):
        self.assertEqual(design.zone_bits([(True, False)]*6), 0x5555)
        self.assertEqual(design.zone_bits([(False, True)]*6), 0xAAAA)
        self.assertEqual(design.zone_bits([(True, True)]*6), 0xFFFF)
        for zone, physical in enumerate(((0, 1, 2), (4,), (5,), (6,), (7,), (3,))):
            for polarity in (0, 1):
                states = [(False, False)]*6
                states[zone] = (polarity == 0, polarity == 1)
                expected = sum(1 << (2*p+polarity) for p in physical)
                self.assertEqual(design.zone_bits(states), expected)

    def test_no_series_resistor_solution_under_5ma_10v_assumptions(self):
        low, high = design.resistor_interval(253, 0.090, 0.005, 10)
        self.assertGreater(low, high)
        self.assertAlmostEqual(high, 1980.198, places=2)

    def test_smaller_input_current_can_admit_a_resistor_interval(self):
        low, high = design.resistor_interval(253, 0.036, 0.0005, 10)
        self.assertLess(low, high)

    def test_led_budget_matches_design_assumptions(self):
        low, high = design.led_current_bounds()
        self.assertGreater(low, 0.005)
        self.assertLess(high, 0.010)

    def test_one_kilohm_wdi_pull_down_with_input_current_budget(self):
        voltage, current = design.watchdog_wdi_budget()
        self.assertAlmostEqual(voltage, 0.1919)
        self.assertLess(voltage, 0.3 * 3.0)
        self.assertLess(current, 0.004)

    def test_ten_kilohms_does_not_meet_same_wdi_low_budget(self):
        voltage, _ = design.watchdog_wdi_budget(resistance=10000)
        self.assertGreater(voltage, 0.3 * 3.0)


if __name__ == "__main__":
    unittest.main()
