# file: settings_manager.py
import json
import os

DEFAULT_FILENAME = "rules_profile.json"

def save_rules(rules_data: list[dict]):
    """Сохраняет список правил в JSON файл."""
    try:
        with open(DEFAULT_FILENAME, 'w', encoding='utf-8') as file:
            json.dump(rules_data, file, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении правил: {e}")
        return False

def load_rules() -> list[dict]:
    """Загружает список правил из JSON файла."""
    if not os.path.exists(DEFAULT_FILENAME):
        # Если файла нет, создаем его с примером
        example_rules = [
            {
                "name": "Сильная перегрузка",
                "enabled": True,
                "parameter": "G",
                "condition": ">",
                "value": 5.0,
                "device_index": 0,
                "action_type": "vibrate",
                "intensity": 0.8
            },
            {
                "name": "Стрельба из пулеметов",
                "enabled": True,
                "parameter": "gun_machinegun",
                "condition": "=",
                "value": 1.0,
                "device_index": 0,
                "action_type": "vibrate",
                "intensity": 0.4
            }
        ]
        save_rules(example_rules)
        return example_rules
        
    try:
        with open(DEFAULT_FILENAME, 'r', encoding='utf-8') as file:
            rules_data = json.load(file)
        return rules_data
    except Exception as e:
        print(f"Ошибка при загрузке правил: {e}")
        return []