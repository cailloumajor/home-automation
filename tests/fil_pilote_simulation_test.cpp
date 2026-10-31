#include "../inc/fil_pilote_simulation.h"

#include <cassert>
#include <cstdint>
#include <initializer_list>

using fil_pilote_simulation::signal;

void expect(int mode, uint32_t elapsed, bool positive, bool negative) {
  const auto actual = signal(mode, elapsed);
  assert(actual.positive == positive);
  assert(actual.negative == negative);
}

int main() {
  // Continuous modes stay stable across cycle boundaries.
  for (const uint32_t elapsed : {0U, 299999U, 300000U, 600001U}) {
    expect(0, elapsed, false, false);
    expect(3, elapsed, true, true);
    expect(4, elapsed, false, true);
    expect(5, elapsed, true, false);
  }
  // Pulses begin immediately, end exactly at their boundary and repeat.
  for (const uint32_t cycle : {0U, 300000U, 600000U}) {
    expect(1, cycle, true, true);
    expect(1, cycle + 2999U, true, true);
    expect(1, cycle + 3000U, false, false);
    expect(1, cycle + 299999U, false, false);
    expect(2, cycle, true, true);
    expect(2, cycle + 6999U, true, true);
    expect(2, cycle + 7000U, false, false);
    expect(2, cycle + 299999U, false, false);
  }
  // Each zone owns its elapsed time, independent of other zones.
  expect(1, 1000U, true, true);
  expect(1, 5000U, false, false);
  // Unsigned subtraction preserves pulse timing through millis() wraparound.
  const uint32_t start = UINT32_MAX - 999U;
  expect(1, uint32_t(1999U - start), true, true);
  expect(1, uint32_t(2000U - start), false, false);
  expect(-1, 0U, true, false);
  expect(6, 0U, true, false);
}
