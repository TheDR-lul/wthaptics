# file: signal_processor.py

class SignalProcessor:
    """Обрабатывает игровые данные на основе набора правил."""
    def __init__(self):
        self.rules: list[dict] = []

    def load_rules(self, rules_data: list[dict]):
        self.rules = rules_data

    def process_game_state(self, game_state: dict) -> list[dict]:
        """
        Анализирует состояние игры и возвращает список действий для устройств.
        """
        actions = []
        for rule in self.rules:
            if not rule.get("enabled", False):
                continue
            
            parameter = rule.get("parameter")
            condition = rule.get("condition")
            target_value = float(rule.get("value"))
            
            current_value = game_state.get(parameter)
            
            if current_value is None:
                continue

            try:
                current_value = float(current_value)
            except (ValueError, TypeError):
                continue

            condition_met = False
            if condition == ">" and current_value > target_value:
                condition_met = True
            elif condition == "<" and current_value < target_value:
                condition_met = True
            elif condition == "=" and current_value == target_value:
                condition_met = True
            
            if condition_met:
                action = {
                    "device_index": rule.get("device_index"),
                    "type": rule.get("action_type"),
                    "intensity": float(rule.get("intensity", 0.5))
                }
                actions.append(action)
        
        return actions