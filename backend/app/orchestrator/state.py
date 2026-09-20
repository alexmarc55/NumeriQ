from dataclasses import dataclass, field

@dataclass
class PipelineState:
    document_id: int
    file_path: str
    company_cui: str | None = None

    doc_type: str | None = None
    extracted_data: dict = field(default_factory=dict)
    proposed_entry: dict | None = None
    validation_flags: list[str] = field(default_factory=list)
    retry_context: list[str] = field(default_factory=list)
    attempt: int = 0
    anomaly_score: float | None = None

    # meta
    status: str = "pending"   # pending / classified / accounted / validated / flagged / done
    errors: list[str] = field(default_factory=list)