import json
from app.agents.base import Agent
from app.orchestrator.state import PipelineState
from app.llm.client import call_openai_text
from app.llm.prompts import ACCOUNTING_PROMPT_TEMPLATE, ACCOUNTING_SCHEMA, FEEDBACK_SECTION_TEMPLATE


class AccountingProposerAgent(Agent):
    name = "accounting_proposer"

    def run(self, state: PipelineState) -> PipelineState:

        feedback_section = ""
        if state.retry_context:
            feedback_section = FEEDBACK_SECTION_TEMPLATE.format(
                issues="\n".join(f"- {f}" for f in state.retry_context)
            )

        prompt = ACCOUNTING_PROMPT_TEMPLATE.format(
            doc_type=state.doc_type,
            extracted_data=json.dumps(state.extracted_data, ensure_ascii=False),
            company_cui=state.company_cui,
            feedback_section=feedback_section,
        )

        raw_response = call_openai_text(prompt, ACCOUNTING_SCHEMA, model="gpt-4o")

        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError:
            state.errors.append(f"{self.name}: raspuns invalid de la model")
            return state

        state.proposed_entry = result
        state.status = "accounted"
        return state