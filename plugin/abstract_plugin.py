import abc
import logging
from typing import NamedTuple, Any

class PluginResult(NamedTuple):
    success: bool
    result: Any
    error_message: str = ""

class AbstractPlugin(abc.ABC):
    @abc.abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def valid(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def init(self, logger: logging.Logger):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, command: str, args: dict) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def cleanup(self):
        raise NotImplementedError

    @abc.abstractmethod
    def status(self) -> Any:
        raise NotImplementedError
