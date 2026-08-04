from abc import ABC, abstractmethod
from app.orchestrator.state import PipelineState

class Agent(ABC):
    name: str

    @abstractmethod
    def run(self, state: PipelineState) -> PipelineState:
        raise NotImplementedError