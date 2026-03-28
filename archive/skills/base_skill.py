from abc import ABC, abstractmethod

class BaseSkill(ABC):
    """
    Abstract base class for all skills.
    Ensures that all skills have a consistent interface for registration and execution.
    """
    def __init__(self, name: str, supported_intents: list):
        self._name = name
        self._supported_intents = supported_intents

    @property
    def name(self) -> str:
        return self._name

    @property
    def supported_intents(self) -> list:
        return self._supported_intents

    @abstractmethod
    def execute(self, intent: str, entity: str, **kwargs) -> str:
        """
        Executes the skill's logic based on the provided intent and entity.
        
        :param intent: The specific intent to handle (e.g., 'open_app').
        :param entity: The target of the intent (e.g., 'notepad').
        :param kwargs: Additional data that might be needed, like file paths or search queries.
        :return: A user-facing string confirming the action or providing information.
        """
        pass
