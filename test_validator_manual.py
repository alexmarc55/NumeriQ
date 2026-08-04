# test_validator_manual.py (rulezi cu python direct, sau ca test)
from app.orchestrator.state import PipelineState
from app.agents.validator import ValidatorAgent

state = PipelineState(
    document_id=999,
    file_path="fake.pdf",
    company_cui="RO12345678",
    doc_type="factura",
    extracted_data={"cui_furnizor": "RO12345678", "suma_totala": 4165, "tva": 665},
    proposed_entry={
        "linii": [
            {"cont": "401", "tip": "debit", "suma": 4165},
            {"cont": "4427", "tip": "debit", "suma": 665},
            {"cont": "704", "tip": "credit", "suma": 3500},
        ],
        "necesita_verificare": False,
        "observatii": None,
    },
)

validator = ValidatorAgent()
result = validator.run(state)
print(result.status)
print(result.validation_flags)

# continuare la test_validator_manual.py, după ce ai result.validation_flags
state.retry_context = result.validation_flags

from app.agents.accounting_proposer import AccountingProposerAgent
proposer = AccountingProposerAgent()
state2 = proposer.run(state)
print(state2.proposed_entry)

validator2 = ValidatorAgent()
result2 = validator2.run(state2)
print(result2.status)
print(result2.validation_flags)