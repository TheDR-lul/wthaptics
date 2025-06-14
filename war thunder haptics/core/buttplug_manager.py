# core/buttplug_manager.py

import asyncio
from buttplug.client import Client
from buttplug.connectors import WebsocketConnector
from buttplug.client import Device

class ButtplugManager:
    def __init__(self):
        self.client: Client | None = None
        self.devices: list[Device] = []
        self.on_devices_updated = None

    async def connect(self, ws_url="ws://localhost:12345"):
        self.client = Client("WarThunderHaptics")
        connector = WebsocketConnector(ws_url)
        await self.client.connect(connector)
        print("[Buttplug] Connected")

        self.client.add_device_added_handler(self._on_device_added)
        self.client.add_device_removed_handler(self._on_device_removed)

        await self.client.start_scanning()
        await asyncio.sleep(1.0)

        self.devices = list(self.client.devices.values())
        if self.on_devices_updated:
            self.on_devices_updated(self.get_devices())

    async def disconnect(self):
        if self.client and self.client.connected:
            await self.client.disconnect()

    async def send_command(self, device_id: str, command_type: str, intensity: float):
        dev = next((d for d in self.client.devices.values() if str(d.index) == device_id), None)
        if not dev:
            print(f"[Buttplug] Device not found: {device_id}")
            return
        print(f"[Buttplug] {dev.name}: {command_type} → {intensity}")
        match command_type:
            case "vibrate" if dev.message_attributes.vibrate:
                await dev.vibrate(intensity)
            case "rotate" if dev.message_attributes.rotate:
                await dev.rotate(intensity)
            case "thrust" if dev.message_attributes.linear:
                await dev.linear(intensity)
            case _:
                print(f"[Buttplug] Unsupported command/type for {dev.name}")

    def get_devices(self):
        return [
            {
                "id": str(dev.index),
                "name": dev.name,
                "types": [
                    t for t in ("vibrate", "rotate", "thrust")
                    if getattr(dev.message_attributes, t)
                ]
            }
            for dev in self.client.devices.values()
        ]

    def _on_device_added(self, client, dev):
        print(f"[Buttplug] Device added: {dev.name}")
        self.devices = list(client.devices.values())
        if self.on_devices_updated:
            self.on_devices_updated(self.get_devices())

    def _on_device_removed(self, client, dev):
        print(f"[Buttplug] Device removed: {dev.name}")
        self.devices = list(client.devices.values())
        if self.on_devices_updated:
            self.on_devices_updated(self.get_devices())
