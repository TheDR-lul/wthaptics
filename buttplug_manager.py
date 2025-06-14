# file: buttplug_manager.py
import asyncio
from buttplug import Client, WebsocketConnector, ButtplugClientDevice
from PyQt6.QtCore import QObject, pyqtSignal

class ButtplugManager(QObject):
    """Управляет подключением и взаимодействием с Buttplug."""
    
    connection_status_changed = pyqtSignal(str)
    devices_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.client = Client("War Thunder Haptics", WebsocketConnector("ws://127.0.0.1:12345"))
        self.client.device_added_handler = self.handle_device_added
        self.client.device_removed_handler = self.handle_device_removed
        self.connected_devices: dict[int, ButtplugClientDevice] = {}

    async def connect(self):
        try:
            self.connection_status_changed.emit("Подключение...")
            await self.client.connect()
            self.connection_status_changed.emit("Подключено. Поиск устройств...")
            await self.client.start_scanning()
        except Exception as e:
            self.connection_status_changed.emit(f"Ошибка: {e}")

    async def disconnect(self):
        await self.client.disconnect()
        self.connection_status_changed.emit("Отключено")

    def handle_device_added(self, device: ButtplugClientDevice):
        self.connected_devices[device.index] = device
        print(f"Устройство добавлено: {device.name}")
        self.devices_updated.emit(self.get_device_list())

    def handle_device_removed(self, device: ButtplugClientDevice):
        if device.index in self.connected_devices:
            del self.connected_devices[device.index]
        print(f"Устройство удалено: {device.name}")
        self.devices_updated.emit(self.get_device_list())

    def get_device_list(self) -> list[str]:
        return [f"{dev.index}: {dev.name}" for dev in self.connected_devices.values()]

    async def execute_action(self, action: dict):
        """Выполняет действие, сгенерированное SignalProcessor."""
        device_index = action.get("device_index")
        device = self.connected_devices.get(device_index)
        if not device:
            return

        action_type = action.get("type")
        intensity = action.get("intensity", 0.0)

        if action_type == "vibrate":
            if "Vibrate" in device.allowed_messages:
                number_of_motors = len(device.vibrate_attrs)
                vibration_levels = [intensity] * number_of_motors
                await device.vibrate(vibration_levels)
        
        elif action_type == "stop":
            await device.stop()