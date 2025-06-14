# file: gui.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QComboBox,
    QLineEdit, QDoubleSpinBox, QCheckBox, QDialog, QDialogButtonBox, QFormLayout
)

class RuleEditorDialog(QDialog):
    """Диалоговое окно для создания и редактирования правил."""
    def __init__(self, rule=None, device_list=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактор правила")
        
        self.device_list = device_list or []
        self.rule_data = rule or {}

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.rule_name = QLineEdit(self.rule_data.get("name", "Новое правило"))
        self.is_enabled = QCheckBox("Правило включено")
        self.is_enabled.setChecked(self.rule_data.get("enabled", True))
        
        self.parameter_name = QLineEdit(self.rule_data.get("parameter", "G"))
        self.parameter_name.setPlaceholderText("Например: G, TAS, M, Wep...")
        
        self.condition = QComboBox()
        self.condition.addItems([">", "<", "="])
        self.condition.setCurrentText(self.rule_data.get("condition", ">"))
        
        self.target_value = QDoubleSpinBox()
        self.target_value.setDecimals(4)
        self.target_value.setRange(-10000.0, 10000.0)
        self.target_value.setValue(float(self.rule_data.get("value", 5.0)))
        
        self.device_selector = QComboBox()
        for device_string in self.device_list:
            try:
                device_id = int(device_string.split(':')[0])
                self.device_selector.addItem(device_string, userData=device_id)
            except (ValueError, IndexError):
                continue
        
        current_device_id = self.rule_data.get("device_index")
        if current_device_id is not None:
            index = self.device_selector.findData(current_device_id)
            if index != -1:
                self.device_selector.setCurrentIndex(index)

        self.action_type = QComboBox()
        self.action_type.addItems(["vibrate", "stop"])
        self.action_type.setCurrentText(self.rule_data.get("action_type", "vibrate"))
        
        self.intensity = QDoubleSpinBox()
        self.intensity.setRange(0.0, 1.0)
        self.intensity.setSingleStep(0.1)
        self.intensity.setValue(float(self.rule_data.get("intensity", 0.8)))

        form_layout.addRow(self.is_enabled)
        form_layout.addRow("Название правила:", self.rule_name)
        form_layout.addRow("Параметр из игры:", self.parameter_name)
        form_layout.addRow("Условие:", self.condition)
        form_layout.addRow("Значение:", self.target_value)
        form_layout.addRow("Устройство:", self.device_selector)
        form_layout.addRow("Действие:", self.action_type)
        form_layout.addRow("Интенсивность:", self.intensity)

        layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_data(self):
        """Возвращает данные правила в виде словаря."""
        return {
            "name": self.rule_name.text(),
            "enabled": self.is_enabled.isChecked(),
            "parameter": self.parameter_name.text(),
            "condition": self.condition.currentText(),
            "value": self.target_value.value(),
            "device_index": self.device_selector.currentData(),
            "action_type": self.action_type.currentText(),
            "intensity": self.intensity.value()
        }


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("War Thunder Haptics Integrator")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_column_layout = QVBoxLayout()
        self.status_label = QLabel("Статус: Ожидание...")
        self.devices_list_widget = QListWidget()
        left_column_layout.addWidget(QLabel("<b>Статус подключения</b>"))
        left_column_layout.addWidget(self.status_label)
        left_column_layout.addWidget(QLabel("<b>Подключенные устройства</b>"))
        left_column_layout.addWidget(self.devices_list_widget)

        right_column_layout = QVBoxLayout()
        right_column_layout.addWidget(QLabel("<b>Конструктор сигналов</b>"))
        
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels(["Вкл", "Название", "Условие", "Действие", "Устройство"])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        buttons_layout = QHBoxLayout()
        self.add_rule_button = QPushButton("Добавить")
        self.edit_rule_button = QPushButton("Редактировать")
        self.delete_rule_button = QPushButton("Удалить")
        buttons_layout.addWidget(self.add_rule_button)
        buttons_layout.addWidget(self.edit_rule_button)
        buttons_layout.addWidget(self.delete_rule_button)
        buttons_layout.addStretch()

        self.save_rules_button = QPushButton("Сохранить профиль")
        self.load_rules_button = QPushButton("Загрузить профиль")
        buttons_layout.addWidget(self.save_rules_button)
        buttons_layout.addWidget(self.load_rules_button)

        right_column_layout.addWidget(self.rules_table)
        right_column_layout.addLayout(buttons_layout)
        
        main_layout.addLayout(left_column_layout, 1)
        main_layout.addLayout(right_column_layout, 3)

    def update_rules_table(self, rules: list[dict]):
        self.rules_table.setRowCount(0)
        for rule in rules:
            row_position = self.rules_table.rowCount()
            self.rules_table.insertRow(row_position)
            
            enabled_checkbox = QCheckBox()
            enabled_checkbox.setChecked(rule.get("enabled", False))
            enabled_checkbox.setDisabled(True)
            self.rules_table.setCellWidget(row_position, 0, enabled_checkbox)

            self.rules_table.setItem(row_position, 1, QTableWidgetItem(rule.get("name", "")))
            condition_string = f"{rule.get('parameter', '')} {rule.get('condition', '')} {rule.get('value', '')}"
            self.rules_table.setItem(row_position, 2, QTableWidgetItem(condition_string))
            action_string = f"{rule.get('action_type', '')} @ {float(rule.get('intensity', 0.0))*100:.0f}%"
            self.rules_table.setItem(row_position, 3, QTableWidgetItem(action_string))
            
            device_id = rule.get('device_index')
            device_name = "Не выбрано"
            for i in range(self.devices_list_widget.count()):
                item = self.devices_list_widget.item(i)
                if item.text().startswith(f"{device_id}:"):
                    device_name = item.text()
                    break
            self.rules_table.setItem(row_position, 4, QTableWidgetItem(device_name))
            
    def update_devices_list(self, devices: list[str]):
        self.devices_list_widget.clear()
        self.devices_list_widget.addItems(devices)