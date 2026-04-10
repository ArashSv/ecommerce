from abc import ABC, abstractmethod
from decimal import Decimal


class BaseGateway(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def get_create_url(self):
        ...

    @abstractmethod
    def get_verify_url(self) -> str:
        ...

    @abstractmethod
    def get_startpay_url(self, trans_id: str) -> str:
        ...

    @abstractmethod
    async def create(self, amount: Decimal, description: str = None, **kwargs) -> dict:
        ...

    @abstractmethod
    async def callback(self, request) -> dict:
        ...

    @abstractmethod
    async def verify(self, transaction_id: str, amount: int) -> dict:
        ...