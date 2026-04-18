import json
import os

CONFIG_PATH = "config.json"

DEFAULT_SERVER = {
    "channels": {
        "world_map":      None,
        "world_events":   None,
        "turn_log":       None,
        "menu":           None,
        "commands":       None,
        "battle_reports": None,
        "leaderboard":    None,
        "public_log":     None,
        "gm_alerts":      None,
        "registration":   None,
    },
    "gm_role":              None,
    "menu_message":         None,
    "registration_message": None,
    "setup_complete":       False,
}

class ConfigManager:
    def __init__(self):
        if not os.path.exists(CONFIG_PATH):
            self._write({})
        self.data = self._read()

    def _read(self):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    def _write(self, data):
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=4)

    def _server(self, guild_id: int) -> dict:
        key = str(guild_id)
        if key not in self.data:
            self.data[key] = json.loads(json.dumps(DEFAULT_SERVER))
            self._write(self.data)
        s = self.data[key]
        if "registration" not in s.get("channels", {}):
            s["channels"]["registration"] = None
        if "registration_message" not in s:
            s["registration_message"] = None
        return s

    def get_channel(self, guild_id: int, name: str):
        return self._server(guild_id)["channels"].get(name)

    def set_channel(self, guild_id: int, name: str, channel_id: int):
        self._server(guild_id)["channels"][name] = channel_id
        self._write(self.data)

    def get_gm_role(self, guild_id: int):
        return self._server(guild_id).get("gm_role")

    def set_gm_role(self, guild_id: int, role_id: int):
        self._server(guild_id)["gm_role"] = role_id
        self._write(self.data)

    def get_menu_message(self, guild_id: int):
        return self._server(guild_id).get("menu_message")

    def set_menu_message(self, guild_id: int, message_id: int):
        self._server(guild_id)["menu_message"] = message_id
        self._write(self.data)

    def get_registration_message(self, guild_id: int):
        return self._server(guild_id).get("registration_message")

    def set_registration_message(self, guild_id: int, message_id: int):
        self._server(guild_id)["registration_message"] = message_id
        self._write(self.data)

    def is_setup_complete(self, guild_id: int) -> bool:
        return self._server(guild_id).get("setup_complete", False)

    def mark_setup_complete(self, guild_id: int):
        self._server(guild_id)["setup_complete"] = True
        self._write(self.data)

    def get_missing_channels(self, guild_id: int):
        return [k for k, v in self._server(guild_id)["channels"].items() if v is None]

    def reset(self, guild_id: int):
        self.data[str(guild_id)] = json.loads(json.dumps(DEFAULT_SERVER))
        self._write(self.data)
