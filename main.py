# file: main.py
import sys
import asyncio
from queue import Queue
from PyQt6.QtWidgets import QApplication
from asyncqt import QEventLoop

from gui import MainWindow, RuleEditorDialog
from buttplug_manager import ButtplugManager
from warthunder_client import WarThunderClient
from signal_processor import SignalProcessor
from settings_manager import load_rules, save_rules

class ApplicationController:
    """Главный класс, связывающий все компоненты."""
    def __init__(self, main_window: MainWindow):
        self.window = main_window
        self.game_data_queue = Queue()
        self.device_list = []
        
        # Инициализация компонентов
        self.buttplug_manager = ButtplugManager()
        self.warthunder_client = WarThunderClient(self.game_data_queue)
        self.signal_processor = SignalProcessor()
        
        # Подключение сигналов к слотам
        self.connect_signals()

        # Загрузка правил при старте
        self.load_rules_profile()
        
    def connect_signals(self):
        """Подключает сигналы от GUI и менеджеров к обработчикам."""
        self.buttplug_manager.connection_status_changed.connect(self.window.status_label.setText)
        self.buttplug_manager.devices_updated.connect(self.handle_devices_update)
        
        self.window.add_rule_button.clicked.connect(self.add_rule)
        self.window.edit_rule_button.clicked.connect(self.edit_rule)
        self.window.delete_rule_button.clicked.connect(self.delete_rule)
        self.window.save_rules_button.clicked.connect(self.save_rules_profile)
        self.window.load_rules_button.clicked.connect(self.load_rules_profile)

    def handle_devices_update(self, devices: list[str]):
        self.device_list = devices
        self.window.update_devices_list(devices)
        self.window.update_rules_table(self.signal_processor.rules)

    def add_rule(self):
        dialog = RuleEditorDialog(device_list=self.device_list, parent=self.window)
        if dialog.exec():
            self.signal_processor.rules.append(dialog.get_data())
            self.window.update_rules_table(self.signal_processor.rules)
            
    def edit_rule(self):
        selected_rows = self.window.rules_table.selectionModel().selectedRows()
        if not selected_rows: return
        row_index = selected_rows[0].row()
        rule_to_edit = self.signal_processor.rules[row_index]
        
        dialog = RuleEditorDialog(rule=rule_to_edit, device_list=self.device_list, parent=self.window)
        if dialog.exec():
            self.signal_processor.rules[row_index] = dialog.get_data()
            self.window.update_rules_table(self.signal_processor.rules)
            
    def delete_rule(self):
        selected_rows = self.window.rules_table.selectionModel().selectedRows()
        if not selected_rows: return
        row_index = selected_rows[0].row()
        del self.signal_processor.rules[row_index]
        self.window.update_rules_table(self.signal_processor.rules)

    def save_rules_profile(self):
        save_rules(self.signal_processor.rules)
        print("Профиль правил сохранен.")

    def load_rules_profile(self):
        rules = load_rules()
        self.signal_processor.load_rules(rules)
        self.window.update_rules_table(self.signal_processor.rules)
        print("Профиль правил загружен.")

    async def main_loop(self):
        """Основной цикл обработки событий."""
        asyncio.create_task(self.buttplug_manager.connect())
        asyncio.create_task(self.warthunder_client.poll_data_loop())
        
        last_actions = {}

        while True:
            if not self.game_data_queue.empty():
                game_state = self.game_data_queue.get()
                
                current_actions = self.signal_processor.process_game_state(game_state)
                
                actions_by_device = {action['device_index']: action for action in current_actions}

                for device_id in self.buttplug_manager.connected_devices.keys():
                    action_to_perform = actions_by_device.get(device_id)
                    last_action = last_actions.get(device_id)

                    if action_to_perform:
                        if action_to_perform != last_action:
                            await self.buttplug_manager.execute_action(action_to_perform)
                            last_actions[device_id] = action_to_perform
                    elif last_action and last_action.get("type") != "stop":
                        stop_action = {"device_index": device_id, "type": "stop"}
                        await self.buttplug_manager.execute_action(stop_action)
                        last_actions[device_id] = stop_action

            await asyncio.sleep(0.05)

if __name__ == "__main__":
    application = QApplication(sys.argv)
    event_loop = QEventLoop(application)
    asyncio.set_event_loop(event_loop)

    main_window = MainWindow()
    controller = ApplicationController(main_window)
    main_window.show()

    with event_loop:
        try:
            event_loop.run_until_complete(controller.main_loop())
        except KeyboardInterrupt:
            print("\nПриложение завершено.")