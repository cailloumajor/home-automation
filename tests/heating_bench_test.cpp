#include "../inc/heating_bench.h"

#include <cassert>
#include <vector>

int main() {
  using fil_pilote_simulation::Signal;
  std::array<Signal, 6> zones{};
  assert(heating_bench::word(zones) == 0);
  zones.fill({true, false});
  assert(heating_bench::word(zones) == 0x5555);
  zones.fill({false, true});
  assert(heating_bench::word(zones) == 0xAAAA);
  zones.fill({true, true});
  assert(heating_bench::word(zones) == 0xFFFF);
  const std::vector<std::vector<int>> mapping = {{0,1,2}, {4}, {5}, {6}, {7}, {3}};
  for (int zone = 0; zone < 6; ++zone) {
    for (int polarity = 0; polarity < 2; ++polarity) {
      zones.fill({false, false});
      zones[zone] = {polarity == 0, polarity == 1};
      uint16_t expected = 0;
      for (int channel : mapping[zone]) expected |= uint16_t(1U << (2*channel+polarity));
      assert(heating_bench::word(zones) == expected);
    }
  }
  // Model the two physical cascaded registers: sample data on rising clock,
  // expose the shift register only on the single rising latch edge.
  for (const uint16_t value : {0U, 1U, 0x8000U, 0x5555U, 0xAAAAU, 0xFFFFU}) {
    bool data = false, clock = false, latch = false;
    uint16_t shift = 0, outputs = 0;
    int clock_edges = 0, latch_edges = 0;
    heating_bench::write(value,
      [&](bool bit) { data = bit; },
      [&](bool bit) {
        if (bit && !clock) { shift = uint16_t((shift << 1) | data); ++clock_edges; }
        clock = bit;
      },
      [&](bool bit) {
        if (bit && !latch) { outputs = shift; ++latch_edges; assert(clock_edges == 16); }
        latch = bit;
      });
    assert(outputs == value);
    assert(clock_edges == 16 && latch_edges == 1);
    assert(!clock && !latch);
  }
}
