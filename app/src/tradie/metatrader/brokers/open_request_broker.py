from abc import ABC, abstractmethod


class OpenRequestBroker(ABC):
    @property
    @abstractmethod
    def request(self): ...

    @property
    @abstractmethod
    def symbol_info(self): ...

    @abstractmethod
    def get_est_margin_initial(self) -> float: ...

    @abstractmethod
    def get_margin_initial(self) -> float: ...

    @abstractmethod
    def get_margin_maintenance(self) -> float: ...

    @abstractmethod
    def get_risk_amount(self) -> float: ...

    @abstractmethod
    def get_position_size_lots(self) -> float: ...

    @abstractmethod
    def get_position_size(self) -> float: ...
