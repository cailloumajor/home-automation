#pragma once

#include <cstdint>
#include <cstdio>
#include <string>

namespace heating_mcp23017_bench {

enum class Fault : uint8_t { NONE, COMMUNICATION, CONFIGURATION };

// LED bench only. RESET_N must have an external pull-down on the real circuit.
// Transport callbacks return success; reads verify latches, not physical loads.
class Controller {
  public:
  bool armed() const { return armed_; }
  Fault fault() const { return fault_; }
  uint16_t last_word() const { return last_word_; }
  std::string fault_detail() const {
    if (fault_ == Fault::NONE) return "NONE";
    char detail[96];
    if (fault_ == Fault::COMMUNICATION)
      std::snprintf(detail, sizeof(detail), "I2C %s reg=0x%02X", writing_ ? "WRITE" : "READ", unsigned(reg_));
    else
      std::snprintf(detail, sizeof(detail), "REGISTER reg=0x%02X expected=0x%04X actual=0x%04X",
                    unsigned(reg_), unsigned(expected_), unsigned(actual_));
    return detail;
  }

  template<typename Reset> void disarm(Reset reset) {
    armed_ = false;
    reset(false);
  }

  template<typename Write, typename Read, typename Reset, typename Pause>
  bool arm(uint16_t word, Write write, Read read, Reset reset, Pause pause) {
    disarm(reset);
    pause(1000);
    reset(true);
    pause(1000);
    const uint8_t control = 0;
    const uint8_t outputs[] = {uint8_t(word), uint8_t(word >> 8)};
    const uint8_t directions[] = {0, 0};
    // Physical reset establishes BANK=0, SEQOP=0. Preload both output latches
    // before either port becomes an output. A and B do not switch atomically.
    if (!write(0x0A, &control, 1)) return fail_(Fault::COMMUNICATION, reset, 0x0A, true);
    if (!write(0x14, outputs, 2)) return fail_(Fault::COMMUNICATION, reset, 0x14, true);
    if (!write(0x00, directions, 2)) return fail_(Fault::COMMUNICATION, reset, 0x00, true);
    if (!verify_(word, read, reset)) return false;
    last_word_ = word;
    fault_ = Fault::NONE;
    armed_ = true;
    return true;
  }

  template<typename Write, typename Read, typename Reset>
  bool refresh(uint16_t word, Write write, Read read, Reset reset) {
    if (!armed_) return false;  // A fault never rearms by itself.
    if (!verify_(last_word_, read, reset)) return false;
    if (word == last_word_) return true;
    const uint8_t outputs[] = {uint8_t(word), uint8_t(word >> 8)};
    if (!write(0x14, outputs, 2)) return fail_(Fault::COMMUNICATION, reset, 0x14, true);
    if (!verify_(word, read, reset)) return false;
    last_word_ = word;
    return true;
  }

  private:
  template<typename Reset>
  bool fail_(Fault fault, Reset reset, uint8_t reg, bool writing = false,
              uint16_t expected = 0, uint16_t actual = 0) {
    fault_ = fault;
    reg_ = reg;
    writing_ = writing;
    expected_ = expected;
    actual_ = actual;
    disarm(reset);
    return false;
  }

  template<typename Read, typename Reset> bool verify_(uint16_t word, Read read, Reset reset) {
    uint8_t control = 0, directions[2]{}, outputs[2]{};
    if (!read(0x0A, &control, 1)) return fail_(Fault::COMMUNICATION, reset, 0x0A);
    if (!read(0x00, directions, 2)) return fail_(Fault::COMMUNICATION, reset, 0x00);
    if (!read(0x14, outputs, 2)) return fail_(Fault::COMMUNICATION, reset, 0x14);
    if (control != 0) return fail_(Fault::CONFIGURATION, reset, 0x0A, false, 0, control);
    const uint16_t direction = uint16_t(directions[0]) | (uint16_t(directions[1]) << 8);
    const uint16_t output = uint16_t(outputs[0]) | (uint16_t(outputs[1]) << 8);
    if (direction != 0) return fail_(Fault::CONFIGURATION, reset, 0x00, false, 0, direction);
    if (output != word) return fail_(Fault::CONFIGURATION, reset, 0x14, false, word, output);
    return true;
  }

  bool armed_{false};
  Fault fault_{Fault::NONE};
  uint16_t last_word_{0};
  uint8_t reg_{0};
  bool writing_{false};
  uint16_t expected_{0}, actual_{0};
};

inline Controller &controller() {
  static Controller instance;
  return instance;
}

}  // namespace heating_mcp23017_bench
