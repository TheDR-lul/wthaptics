from dataclasses import dataclass, field
from typing import List

@dataclass
class Action:
    device: str           # Название/ID устройства
    type: str             # 'vibrate', 'rotate', 'thrust', ...
    intensity: str        # Строковое выражение (например, 'min(1.0, (G-1)/6)')

@dataclass
class Rule:
    name: str
    enabled: bool
    condition: str        # Строковое выражение (например, '(G > 4) and (speed > 400)')
    actions: List[Action]

@dataclass
class Profile:
    rules: List[Rule]

@dataclass
class Device:
    id: str
    name: str
    types: List[str]      # Доступные типы команд
    connected: bool = False
