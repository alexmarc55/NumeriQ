from app.orchestrator.state import PipelineState
from app.agents.document_classifier import DocumentClassifierAgent
from app.agents.accounting_proposer import AccountingProposerAgent
from app.agents.validator import ValidatorAgent

TRANSACTIONAL_DOC_TYPES = {
    "factura", "factura_storno", "bon_fiscal", "chitanta",
    "extras_cont_bancar", "ordin_plata",
}

MAX_RETRIES = 3

class Orchestrator:
    def __init__(self):
        self.classifier = DocumentClassifierAgent()
        self.accounting_proposer = AccountingProposerAgent()
        self.validator = ValidatorAgent()

    def run(self, document_id: int, file_path: str, company_cui: str) -> PipelineState:
        state = PipelineState(document_id=document_id, file_path=file_path, company_cui=company_cui)

        state = self.classifier.run(state)
        if state.errors:
            state.status = "failed"
            return state

        if state.doc_type in TRANSACTIONAL_DOC_TYPES:

            for attempt in range(MAX_RETRIES):
                state.attempt = attempt + 1
                state = self.accounting_proposer.run(state)
                if state.errors:
                    state.status = "failed"
                    return state

                state = self.validator.run(state)
                if state.errors:
                    state.status = "failed"
                    return state

                if not state.validation_flags:
                    break

                state.retry_context = state.validation_flags
        else:
            state.status = "classified_only"

        return state