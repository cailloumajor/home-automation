#pragma once

#include <array>
#include <cstdint>
#include "fil_pilote_simulation.h"

namespace heating_bench {

// Bench only: six software zones map to eight pairs of indicator LEDs.
inline uint16_t word(const std::array<fil_pilote_simulation::Signal, 6> &zones) {
  constexpr uint8_t mapping[] = {0, 0, 0, 5, 1, 2, 3, 4};
  uint16_t result = 0;
  for (uint8_t channel = 0; channel < 8; ++channel) {
    const auto &signal = zones[mapping[channel]];
    if (signal.positive) result |= uint16_t(1U << (2 * channel));
    if (signal.negative) result |= uint16_t(1U << (2 * channel + 1));
  }
  return result;
}

// One complete word, MSB first, then one latch pulse: no intermediate states.
// Callbacks on the real bench provide a short settling delay after each edge.
template<typename Data, typename Clock, typename Latch>
void write(uint16_t value, Data data, Clock clock, Latch latch) {
  latch(false);
  clock(false);
  for (int bit = 15; bit >= 0; --bit) {
    data((value & (uint16_t(1U) << bit)) != 0);
    clock(true);
    clock(false);
  }
  latch(true);
  latch(false);
}

}  // namespace heating_bench
