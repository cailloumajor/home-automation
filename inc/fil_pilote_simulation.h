#pragma once

#include <cstdint>

namespace fil_pilote_simulation {

// Logical polarity envelopes, never physical output pins or 50 Hz generation.
struct Signal {
  bool positive;
  bool negative;
};

// Mode indices match the options in heating_zone.yaml. A changed mode starts
// a fresh cycle. Unsigned elapsed time also handles the millis() wraparound.
inline Signal signal(int mode, uint32_t elapsed_ms) {
  const uint32_t phase = elapsed_ms % 300000U;
  switch (mode) {
    case 0: return {false, false};  // Confort
    case 1: return {phase < 3000U, phase < 3000U};
    case 2: return {phase < 7000U, phase < 7000U};
    case 3: return {true, true};    // Eco
    case 4: return {false, true};   // Hors-gel
    default: return {true, false}; // Arret, including invalid indices
  }
}

}  // namespace fil_pilote_simulation
