import asyncio
import logging
from buttplug.client import Client, Device
from buttplug.connectors import WebsocketConnector
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger("buttplug")

class ButtplugManager(QObject):
    connection_status_changed = pyqtSignal(str)
    devices_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.connector = WebsocketConnector("ws://192.168.2.149:12345")
        self.client = Client("War Thunder Haptics")
        self.client.device_added_handler = self.handle_device_added
        self.client.device_removed_handler = self.handle_device_removed
        self.connected_devices: dict[int, Device] = {}

    async def connect(self):
        try:
            self.connection_status_changed.emit("Подключение...")
            await self.client.connect(self.connector)
            self.connection_status_changed.emit("Подключено. Поиск устройств...")
            await self.client.start_scanning()
            asyncio.create_task(self.auto_rescan())
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            self.connection_status_changed.emit(f"Ошибка: {e}")

    async def auto_rescan(self):
        while True:
            try:
                await asyncio.sleep(5)
                await self.client.start_scanning()
            except Exception as e:
                logger.error(f"Ошибка автосканирования: {e}")
                break

    async def disconnect(self):
        await self.client.disconnect()
        self.connection_status_changed.emit("Отключено")

    async def handle_device_added(self, device: Device):
        self.connected_devices[device.index] = device
        logger.info(f"DEVICE ADDED: {device.index}: {device.name}")
        QTimer.singleShot(0, self._emit_devices_updated)

    async def handle_device_removed(self, device: Device):
        if device.index in self.connected_devices:
            del self.connected_devices[device.index]
        logger.info(f"DEVICE REMOVED: {device.index}: {device.name}")
        QTimer.singleShot(0, self._emit_devices_updated)

    def _emit_devices_updated(self):
        device_strs = self.get_device_list()
        if device_strs:
            logger.info("DEVICES: " + "; ".join(device_strs))
        self.devices_updated.emit(device_strs)

    def get_device_list(self) -> list[str]:
        return [f"{dev.index}: {dev.name}" for dev in self.connected_devices.values()]

    async def execute_action(self, action: dict):
        device_index = action.get("device_index")
        device = self.connected_devices.get(device_index)
        if not device:
            logger.warning(f"Нет устройства с индексом {device_index}")
            return

        action_type = action.get("type")
        intensity = action.get("intensity", 0.0)

        if action_type == "vibrate":
            allowed = getattr(device, "allowed_messages", None)
            if allowed and "Vibrate" in allowed:
                num_motors = allowed["Vibrate"].feature_count or 1
                vibration_levels = [intensity] * num_motors
                await device.vibrate(vibration_levels)
        elif action_type == "stop":
            await device.stop()
