from abc import ABC, abstractmethod

class BaseCheckinHandler(ABC):

    @abstractmethod
    async def execute(self, payload):
        pass