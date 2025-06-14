import json
from .models import Profile, Rule, Action

class ProfileManager:
    @staticmethod
    def load_profile(path: str) -> Profile:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        rules = [Rule(
            name=r["name"],
            enabled=r.get("enabled", True),
            condition=r["condition"],
            actions=[Action(**a) for a in r["actions"]]
        ) for r in data["rules"]]
        return Profile(rules=rules)

    @staticmethod
    def save_profile(profile: Profile, path: str):
        data = {
            "rules": [
                {
                    "name": rule.name,
                    "enabled": rule.enabled,
                    "condition": rule.condition,
                    "actions": [a.__dict__ for a in rule.actions]
                } for rule in profile.rules
            ]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
