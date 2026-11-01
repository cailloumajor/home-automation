#include "../inc/heating_mcp23017_bench.h"

#include <algorithm>
#include <array>
#include <cassert>
#include <string>
#include <vector>

using heating_mcp23017_bench::Controller;
using heating_mcp23017_bench::Fault;

struct Bus {
  std::array<uint8_t, 32> registers{};
  bool released{false};
  int operations{0};
  int fail_at{-1};
  bool ignore_direction_write{false};
  bool partial_write{false};
  std::vector<std::string> events;

  void reset(bool release) {
    released = release;
    events.push_back(release ? "release" : "reset");
    if (!release) {
      registers.fill(0);
      registers[0] = registers[1] = 0xFF;
    }
  }
  bool write(uint8_t reg, const uint8_t *bytes, uint8_t len) {
    events.push_back("write:" + std::to_string(reg));
    if (!released || ++operations == fail_at) return false;
    if (ignore_direction_write && reg == 0) return true;
    if (partial_write && reg == 0x14) {
      registers[reg] = bytes[0];
      return false;
    }
    for (uint8_t i = 0; i < len; ++i) registers[reg+i] = bytes[i];
    return true;
  }
  bool read(uint8_t reg, uint8_t *bytes, uint8_t len) {
    if (!released || ++operations == fail_at) return false;
    for (uint8_t i = 0; i < len; ++i) bytes[i] = registers[reg+i];
    return true;
  }
};

bool arm(Controller &controller, Bus &bus, uint16_t value) {
  return controller.arm(value,
    [&](uint8_t reg, const uint8_t *bytes, uint8_t len) { return bus.write(reg, bytes, len); },
    [&](uint8_t reg, uint8_t *bytes, uint8_t len) { return bus.read(reg, bytes, len); },
    [&](bool release) { bus.reset(release); },
    [&](uint32_t us) { assert(us >= 1); bus.events.push_back("wait"); });
}

bool refresh(Controller &controller, Bus &bus, uint16_t value) {
  return controller.refresh(value,
    [&](uint8_t reg, const uint8_t *bytes, uint8_t len) { return bus.write(reg, bytes, len); },
    [&](uint8_t reg, uint8_t *bytes, uint8_t len) { return bus.read(reg, bytes, len); },
    [&](bool release) { bus.reset(release); });
}

int main() {
  // Reset and preload must precede enabling either output port.
  for (uint16_t value : {0U, 0xFFFFU, 0x5555U, 0xAAAAU, 0xB100U, 0x4E00U}) {
    Controller controller;
    Bus bus;
    assert(!controller.armed() && controller.fault() == Fault::NONE);
    assert(arm(controller, bus, value));
    assert(controller.armed() && bus.released && controller.last_word() == value);
    const std::vector<std::string> expected = {"reset", "wait", "release", "wait",
        "write:10", "write:20", "write:0"};
    assert(bus.events == expected);
    assert(bus.registers[0] == 0 && bus.registers[1] == 0);
    assert(bus.registers[0x14] == uint8_t(value));
    assert(bus.registers[0x15] == uint8_t(value >> 8));
  }

  // Every failed initialization transaction must assert hardware reset.
  for (int operation = 1; operation <= 6; ++operation) {
    Controller controller;
    Bus bus;
    bus.fail_at = operation;
    assert(!arm(controller, bus, 0x5555));
    assert(!controller.armed() && !bus.released && controller.fault() == Fault::COMMUNICATION);
    const std::string details[] = {"I2C WRITE reg=0x0A", "I2C WRITE reg=0x14", "I2C WRITE reg=0x00",
        "I2C READ reg=0x0A", "I2C READ reg=0x00", "I2C READ reg=0x14"};
    assert(controller.fault_detail() == details[operation - 1]);
    const int before = bus.operations;
    assert(!refresh(controller, bus, 0xFFFF));
    assert(bus.operations == before && !bus.released);
  }

  // An acknowledged but ineffective configuration must not report activation.
  {
    Controller controller;
    Bus bus;
    bus.ignore_direction_write = true;
    assert(!arm(controller, bus, 0x5555));
    assert(!bus.released && controller.fault() == Fault::CONFIGURATION);
  }

  // Every failed refresh transaction, including verification after a write,
  // must disable the device without committing the new cached command.
  for (int operation = 1; operation <= 7; ++operation) {
    Controller controller;
    Bus bus;
    assert(arm(controller, bus, 0x5555));
    bus.operations = 0;
    bus.fail_at = operation;
    assert(!refresh(controller, bus, 0xAAAA));
    assert(!bus.released && !controller.armed());
    assert(controller.last_word() == 0x5555 && controller.fault() == Fault::COMMUNICATION);
    const std::string details[] = {"I2C READ reg=0x0A", "I2C READ reg=0x00", "I2C READ reg=0x14",
        "I2C WRITE reg=0x14", "I2C READ reg=0x0A", "I2C READ reg=0x00", "I2C READ reg=0x14"};
    assert(controller.fault_detail() == details[operation - 1]);
  }

  // A brief external reset between polls is detected even if I2C works again.
  {
    Controller controller;
    Bus bus;
    assert(arm(controller, bus, 0xFFFF));
    bus.reset(false);
    bus.reset(true);
    assert(!refresh(controller, bus, 0xFFFF));
    assert(controller.fault() == Fault::CONFIGURATION && !bus.released);
    assert(controller.fault_detail() == "REGISTER reg=0x00 expected=0x0000 actual=0xFFFF");
    const std::string captured = controller.fault_detail();
    assert(!refresh(controller, bus, 0xFFFF));
    assert(controller.fault_detail() == captured);  // Hardware reset must not erase the evidence.
    assert(arm(controller, bus, 0x5555));  // Explicit retry is the only recovery.
    assert(controller.fault() == Fault::NONE && controller.armed());
    assert(controller.fault_detail() == "NONE");
  }

  // A changed latch or control register is not accepted as the requested state.
  for (uint8_t reg : {0x0AU, 0x14U, 0x15U}) {
    Controller controller;
    Bus bus;
    assert(arm(controller, bus, 0x5555));
    bus.registers[reg] ^= 1;
    assert(!refresh(controller, bus, 0x5555));
    assert(controller.fault() == Fault::CONFIGURATION && !bus.released);
    const std::string expected = reg == 0x0A ? "REGISTER reg=0x0A expected=0x0000 actual=0x0001" :
        reg == 0x14 ? "REGISTER reg=0x14 expected=0x5555 actual=0x5554" :
                      "REGISTER reg=0x14 expected=0x5555 actual=0x5455";
    assert(controller.fault_detail() == expected);
  }

  // Loss of the second byte must also reset an already partially updated port.
  {
    Controller controller;
    Bus bus;
    assert(arm(controller, bus, 0x5555));
    bus.partial_write = true;
    assert(!refresh(controller, bus, 0xAAAA));
    assert(!bus.released && !controller.armed());
  }

  // An unchanged word is still checked, but does not generate another write.
  {
    Controller controller;
    Bus bus;
    assert(arm(controller, bus, 0x5555));
    bus.events.clear();
    assert(refresh(controller, bus, 0x5555));
    assert(bus.events.empty());
    assert(refresh(controller, bus, 0xAAAA));
    assert(controller.last_word() == 0xAAAA);
    controller.disarm([&](bool release) { bus.reset(release); });
    assert(!bus.released && !controller.armed());
  }
}
