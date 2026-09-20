from app.agents.base import Agent
from app.orchestrator.state import PipelineState
from app.llm.client import call_openai_with_document
from app.llm.prompts import CLASSIFICATION_PROMPT, CLASSIFICATION_SCHEMA
import json

class DocumentClassifierAgent(Agent):
    name = "document_classifier"

    def run(self, state: PipelineState) -> PipelineState:
        raw_response = call_openai_with_document(
            state.file_path, CLASSIFICATION_PROMPT, CLASSIFICATION_SCHEMA
        )
        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError:
            state.errors.append(f"{self.name}: invalid response from LLM")
            return state

        state.doc_type = result.get("doc_type")
        state.extracted_data = result
        state.status = "classified"
        return state