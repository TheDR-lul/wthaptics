from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, buttplug_manager, profile_manager):
        super().__init__()
        self.setWindowTitle("War Thunder Haptics Integrator")
        self.buttplug_manager = buttplug_manager
        self.profile_manager = profile_manager
        self.devices = []
        self.init_ui()

    def init_ui(self):
        main = QWidget()
        layout = QVBoxLayout()

        # Статус
        self.status_label = QLabel("Status: Not connected")
        layout.addWidget(self.status_label)

        # Список устройств
        layout.addWidget(QLabel("Устройства:"))
        self.device_list = QListWidget()
        layout.addWidget(self.device_list)

        # Кнопка теста устройства
        self.test_btn = QPushButton("Тестировать выбранное устройство")
        self.test_btn.clicked.connect(self.test_device)
        layout.addWidget(self.test_btn)

        # Кнопка загрузки профиля
        self.load_btn = QPushButton("Загрузить профиль")
        self.load_btn.clicked.connect(self.load_profile)
        layout.addWidget(self.load_btn)

        main.setLayout(layout)
        self.setCentralWidget(main)

    def update_devices(self, devices):
        self.device_list.clear()
        self.devices = devices
        for d in devices:
            self.device_list.addItem(f"{d['name']} ({', '.join(d['types'])})")

    def test_device(self):
        idx = self.device_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите устройство")
            return
        dev = self.devices[idx]
        # Отправим тестовую команду (0.5 интенсивность)
        # Можно await, но PyQt слот не поддерживает - for demo:
        import asyncio
        asyncio.create_task(self.buttplug_manager.send_command(dev["id"], dev["types"][0], 0.5))

    def load_profile(self):
        QMessageBox.information(self, "Загрузка профиля", "Эта функция будет реализована позже.")
