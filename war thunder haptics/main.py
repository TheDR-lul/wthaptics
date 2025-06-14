import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.buttplug_manager import ButtplugManager
from core.profile import ProfileManager

def main():
    app = QApplication(sys.argv)

    # Запускаем менеджеры
    buttplug_manager = ButtplugManager()
    profile_manager = ProfileManager()

    # GUI
    window = MainWindow(buttplug_manager, profile_manager)
    window.show()

    # Async инициализация устройств
    async def init_devices():
        await buttplug_manager.connect()
        window.update_devices(buttplug_manager.get_devices())

    loop = asyncio.get_event_loop()
    loop.create_task(init_devices())

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
