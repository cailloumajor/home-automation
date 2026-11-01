# Esplinky TIC investigation — parked work

## Scope and firmware

Work archived on `esplinky/tic-diagnostic` on 2026-11-01.
The regular firmware is `esplinky.yaml`. The temporary entry point,
`esplinky_diagnostic.yaml`, adds USB logs, UART delimiter counts and two
hardware edge counters on GPIO13, with and without a 13 us PCNT filter.
The PCNT filter affects counting only; it does not filter the UART input.
Thread network settings and secret references are preserved.

Both entry points were validated and compiled with ESPHome 2026.10.1.
The user requested restoration of the regular firmware before parking this work.

## Observations

The Super Mini ESP32-H2 uses GPIO13 RX, 9600 baud, 7E1, standard TIC mode,
and a 30-second acquisition interval. The user confirmed that the board
was not physically moved.

With the homemade interface, one restart produced the first readings after
113 seconds and the off-peak energy reading after 163 seconds. Apparent power
and its ratio still had no state after 227 seconds, although the API was online.

The software capture often received `42` instead of the expected `02` frame
start and many `0E` bytes instead of `0A` group separators. Hardware counters
reported approximately 3000 rising edges/s without filtering and 1370/s with
a 13 us PCNT filter, indicating short pulses at the input.

A temporary alternating GPIO filter test, with a threshold around 1.8 us,
did not improve reception and produced incoherent bytes and a checksum error.
The filter test and its helper were removed, including all boot automation.

## WeMos-TIC V1.2 comparison

The user connected the same H2 to a WeMos-TIC V1.2 using jumper wires,
keeping the same firmware and Thread network.

During a 75-second observation, all six exposed sensors published together
three times, at approximately 30-second intervals. Frame boundaries were
correct. Two acquisitions contained 873 bytes, each with 38 LF and 38 CR,
without SI or SO. The third had 31 LF and 31 CR and one checksum error;
all six sensors still published. Reception was better, but not error-free.
The time from physical startup was not measured in this comparison.

Across 38 samples, average edge rates were 1497/s raw and 1381/s filtered.
This points toward the homemade interface or its wiring, without isolating
one particular component.

## Hardware

The homemade Horizon EDA project was supplied separately by the user and
was not modified during this investigation.

| Function | Homemade interface | WeMos-TIC V1.2 |
| --- | --- | --- |
| Optocoupler | LTV-814S | LTV-814 |
| MOSFET | 2N7002 | BSS138 |
| Gate-to-ground resistor | 3.3 kOhm | 3.3 kOhm |
| Output pull-up to 3.3 V | 10 kOhm | 10 kOhm |
| TIC input resistor | Fixed 1.2 kOhm | Adjustable, 2 kOhm |

Different MOSFET gate-drive margins are a hypothesis, not a confirmed cause.
The manufacturer of the fitted transistor was not confirmed. The user has
neither an oscilloscope nor a logic analyzer.

## Parked options

- Replace only Q1 with a suitable BSS138 and repeat the comparison. The expected
  SOT-23 pin mapping is 1 = gate, 2 = source, 3 = drain. No replacement was made.
- Keep the H2 and build a D1 mini adapter to replace the jumper wires. Route
  3.3 V, GND and the shield TIC output to GPIO13. Use removable sockets and
  leave USB-C accessible. Do not connect both interface outputs to GPIO13.
- Consider the xyzroe/Mind House ESP32 C6 D1. It advertises D1 shield support
  and Thread, but was out of stock when checked. Shield pin compatibility
  still needs verification, and ESPHome must be rebuilt for the C6.

The adapter has not been designed. Its preliminary budget was EUR 10–25
including delivery for five bare PCBs and connectors for one adapter,
excluding tools. This was not a manufacturing quote.

## References

- [WeMos-TIC](https://github.com/hallard/WeMos-TIC)
- [ESP32 C6 D1](https://github.com/xyzroe/ESP32_C6_D1)
- [BSS138 example datasheet](https://www.diodes.com/_files/datasheets/BSS138.pdf)
- [2N7002 example datasheet](https://www.diodes.com/_files/datasheets/2N7002.pdf)

## Resuming

The retained hardware is the H2 connected to the WeMos-TIC V1.2 by jumper wires.
Confirm the installed firmware and reading cadence before new experiments.
Secrets and Thread datasets remain local and must not be copied into this file.
