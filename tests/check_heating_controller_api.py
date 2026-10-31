"""On-device V0.2 check: changes simulated modes, then restarts the controller.

Run with ESPHome's Python environment from the repository root.
Requires aioesphomeapi and PyYAML, already supplied by ESPHome.
Reads the local API key without printing it. Never use on physical outputs.
"""

import asyncio
from pathlib import Path

import yaml
from aioesphomeapi import APIClient
from aioesphomeapi.model import BinarySensorInfo, ButtonInfo, SelectInfo


OPTIONS = ["Confort", "Confort -1 °C", "Confort -2 °C", "Éco", "Hors-gel", "Arrêt"]
INITIAL_SIGNALS = [(False, False), (True, True), (True, True),
                    (True, True), (False, True), (True, False)]


async def wait_for(predicate, timeout=15):
    async with asyncio.timeout(timeout):
        while not predicate():
            await asyncio.sleep(0.1)


async def connect(key):
    client = APIClient("heating-controller.local", 6053, noise_psk=key,
                        client_info="V0.2 simulation verification")
    await client.connect(login=True)
    entities, _ = await client.list_entities_services()
    states = {}
    client.subscribe_states(lambda state: states.__setitem__(state.key, state.state))
    return client, entities, states


async def main():
    key = yaml.safe_load(Path("secrets.yaml").read_text())["api_key_heating_controller"]
    client, entities, states = await connect(key)
    selects = [e for e in entities if isinstance(e, SelectInfo)]
    sensors = [e for e in entities if isinstance(e, BinarySensorInfo)]
    assert len(selects) == 6 and len(sensors) == 12
    assert all(e.options == OPTIONS for e in selects)
    pairs = {}
    for select in selects:
        zone = select.name.removesuffix(" mode")
        pairs[select.key] = tuple(next(e.key for e in sensors if e.name ==
            f"{zone} simulation alternance {polarity}")
            for polarity in ("positive", "négative"))

    async def check(select, option, signal):
        client.select_command(select.key, option)
        positive, negative = pairs[select.key]
        await wait_for(lambda: states.get(select.key) == option
                        and states.get(positive) == signal[0]
                        and states.get(negative) == signal[1])

    try:
        await wait_for(lambda: all(states.get(e.key) == "Arrêt" for e in selects))
        for select in selects:
            for option, signal in zip(OPTIONS, INITIAL_SIGNALS):
                await check(select, option, signal)
                await wait_for(lambda: all(states.get(e.key) == "Arrêt"
                    for e in selects if e.key != select.key))
            print(f"Six modes et indépendance : {select.name} OK", flush=True)

        select = selects[0]
        positive, negative = pairs[select.key]
        for option, duration in [(OPTIONS[1], 3), (OPTIONS[2], 7)]:
            await check(select, option, (True, True))
            await asyncio.sleep(duration + 0.5)
            await wait_for(lambda: states.get(positive) is False
                            and states.get(negative) is False)
            print(f"Fin d'impulsion {duration} s : OK", flush=True)

        # Leave non-default modes before restarting to verify reset policy.
        for select in selects:
            await check(select, "Éco", (True, True))
        restart = next(e for e in entities if isinstance(e, ButtonInfo))
        client.button_command(restart.key)
        await asyncio.sleep(2)
    finally:
        await client.disconnect()

    for attempt in range(12):
        try:
            client, entities, states = await connect(key)
            break
        except Exception:
            if attempt == 11:
                raise
            await asyncio.sleep(2)
    try:
        await wait_for(lambda: all(states.get(e.key) == "Arrêt" for e in selects))
        await wait_for(lambda: all(states.get(p) is True and states.get(n) is False
                                    for p, n in pairs.values()))
        print("Reconnexion et retour des six zones à Arrêt : OK", flush=True)
    finally:
        await client.disconnect()


asyncio.run(main())
