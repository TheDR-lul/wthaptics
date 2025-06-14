import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
)

import sys
import asyncio
from queue import Queue
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from gui import MainWindow, RuleEditorDialog
from buttplug_manager import ButtplugManager
from warthunder_client import WarThunderClient
from signal_processor import SignalProcessor
from settings_manager import load_rules, save_rules

logger = logging.getLogger("app")

class ApplicationController:
    def __init__(self, main_window: MainWindow):
        self.window = main_window
        self.game_data_queue = Queue()
        self.device_list = []
        self.buttplug_manager = ButtplugManager()
        self.warthunder_client = WarThunderClient(self.game_data_queue)
        self.signal_processor = SignalProcessor()
        self.connect_signals()
        self.load_rules_profile()
        
    def connect_signals(self):
        self.buttplug_manager.connection_status_changed.connect(self.window.status_label.setText)
        self.buttplug_manager.devices_updated.connect(self.handle_devices_update)
        self.window.add_rule_button.clicked.connect(self.add_rule)
        self.window.edit_rule_button.clicked.connect(self.edit_rule)
        self.window.delete_rule_button.clicked.connect(self.delete_rule)
        self.window.save_rules_button.clicked.connect(self.save_rules_profile)
        self.window.load_rules_button.clicked.connect(self.load_rules_profile)

    def handle_devices_update(self, devices: list[str]):
        logger.info(f"DEVICES: {', '.join(devices) if devices else 'нет устройств'}")
        self.device_list = devices
        self.window.update_devices_list(devices)
        self.window.update_rules_table(self.signal_processor.rules)

    def add_rule(self):
        dialog = RuleEditorDialog(device_list=self.device_list, parent=self.window)
        if dialog.exec():
            rule = dialog.get_data()
            logger.info(f"ADD RULE: {rule}")
            self.signal_processor.rules.append(rule)
            self.window.update_rules_table(self.signal_processor.rules)
            
    def edit_rule(self):
        selected_rows = self.window.rules_table.selectionModel().selectedRows()
        if not selected_rows: return
        row_index = selected_rows[0].row()
        rule_to_edit = self.signal_processor.rules[row_index]
        dialog = RuleEditorDialog(rule=rule_to_edit, device_list=self.device_list, parent=self.window)
        if dialog.exec():
            rule = dialog.get_data()
            logger.info(f"EDIT RULE: {rule}")
            self.signal_processor.rules[row_index] = rule
            self.window.update_rules_table(self.signal_processor.rules)
            
    def delete_rule(self):
        selected_rows = self.window.rules_table.selectionModel().selectedRows()
        if not selected_rows: return
        row_index = selected_rows[0].row()
        logger.info(f"DELETE RULE index: {row_index}")
        del self.signal_processor.rules[row_index]
        self.window.update_rules_table(self.signal_processor.rules)

    def save_rules_profile(self):
        save_rules(self.signal_processor.rules)
        logger.info("RULES PROFILE SAVED")

    def load_rules_profile(self):
        rules = load_rules()
        self.signal_processor.load_rules(rules)
        self.window.update_rules_table(self.signal_processor.rules)
        logger.info("RULES PROFILE LOADED")

    async def main_loop(self):
        logger.info("MAIN LOOP START")
        asyncio.create_task(self.buttplug_manager.connect())
        asyncio.create_task(self.warthunder_client.poll_data_loop())
        last_actions = {}

        while True:
            if not self.game_data_queue.empty():
                game_state = self.game_data_queue.get()
                logger.debug(f"NEW GAME STATE: {game_state}")
                current_actions = self.signal_processor.process_game_state(game_state)
                logger.debug(f"ACTIONS: {current_actions}")
                actions_by_device = {action['device_index']: action for action in current_actions}

                for device_id in self.buttplug_manager.connected_devices.keys():
                    action_to_perform = actions_by_device.get(device_id)
                    last_action = last_actions.get(device_id)

                    if action_to_perform:
                        if action_to_perform != last_action:
                            logger.info(f"EXEC ACTION for device {device_id}: {action_to_perform}")
                            await self.buttplug_manager.execute_action(action_to_perform)
                            last_actions[device_id] = action_to_perform
                    elif last_action and last_action.get("type") != "stop":
                        stop_action = {"device_index": device_id, "type": "stop"}
                        logger.info(f"STOP device {device_id}")
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
            logger.info("Приложение завершено.")
