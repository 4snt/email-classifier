import json
import os
from typing import Optional, Dict
from app.domain.ports import ProfilePort

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/profiles.json")

class JsonProfileAdapter(ProfilePort):
    def __init__(self, path: str = DATA_PATH):
        with open(path, "r") as f:
            self.profiles = json.load(f)

    def get_profile(self, profile_id: str) -> Optional[Dict]:
        return self.profiles.get(profile_id)
