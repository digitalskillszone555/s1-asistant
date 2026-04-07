# skills/router.py
# S1 Assistant - Skills Router
# Focus: Discovery and listing of available skills.

from skills import time, date, weather, system_info

class Skill:
    def __init__(self, name, module):
        self.name = name
        self.module = module

class SkillsRouter:
    """
    Main router for listing and managing S1 Assistant skills.
    """
    def __init__(self):
        # In a more advanced version, this could be dynamic discovery
        self.skills = [
            Skill("web_actions", None),
            Skill("file_actions", None),
            Skill("app_resolver", None)
        ]
        
        # Legacy functional skills
        self.legacy_skills = {
            "time": time,
            "date": date,
            "weather": weather,
            "system_info": system_info
        }

def get_skills_router():
    return SkillsRouter()
