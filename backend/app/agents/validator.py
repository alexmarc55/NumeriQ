from app.agents.base import Agent
from app.orchestrator.state import PipelineState

TVA_RATES_VALIDE = {0, 5, 9, 19}


class ValidatorAgent(Agent):
    name = "validator"

    def run(self, state: PipelineState) -> PipelineState:
        if not state.proposed_entry:
            return state

        linii = state.proposed_entry.get("linii", [])
        flags = []

        # 1. Balanta debit = credit
        total_debit = sum(l["suma"] for l in linii if l["tip"] == "debit")
        total_credit = sum(l["suma"] for l in linii if l["tip"] == "credit")
        if abs(total_debit - total_credit) > 0.01:
            flags.append(
                f"Balanta incorecta: debit={total_debit}, credit={total_credit}"
            )

        # 2. Coerenta conturilor cu direcția operațiunii
        conturi = {l["cont"] for l in linii}
        cui_firma = state.company_cui
        cui_furnizor = state.extracted_data.get("cui_furnizor")

        if cui_firma and cui_furnizor:
            este_venit = cui_firma == cui_furnizor
            if este_venit and ("401" in conturi or "4426" in conturi):
                flags.append(
                    "Conturi de cheltuiala/furnizor (401/4426) folosite pentru o operatiune de venit"
                )
            if not este_venit and ("4111" in conturi or "704" in conturi or "706" in conturi):
                flags.append(
                    "Conturi de venit (4111/704/706) folosite pentru o operatiune de cheltuiala"
                )

        # 3. Rata TVA plauzibila
        suma_totala = state.extracted_data.get("suma_totala")
        tva = state.extracted_data.get("tva")
        if suma_totala and tva is not None and suma_totala > tva:
            suma_neta = suma_totala - tva
            rata_calculata = round((tva / suma_neta) * 100) if suma_neta else None
            if rata_calculata is not None and rata_calculata not in TVA_RATES_VALIDE:
                flags.append(
                    f"Rata TVA neobisnuita: {rata_calculata}% (suma_totala={suma_totala}, tva={tva})"
                )

        # 4. Conturi valide (doar numeric)
        for l in linii:
            if not l["cont"].isdigit():
                flags.append(f"Cont invalid (nu e numeric): {l['cont']}")

        state.validation_flags = flags

        if flags:
            state.proposed_entry["necesita_verificare"] = True
            state.status = "needs_review"
        else:
            state.status = "validated"

        return state