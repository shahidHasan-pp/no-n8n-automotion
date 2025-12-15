
import abc

class MessagingStrategy(abc.ABC):
    @abc.abstractmethod
    def send(self, to: str, content: str, link: str = None, extra_data: dict = None) -> bool:
        pass
