from pydantic import BaseModel
from typing import List

# Pydantic model for TherapeuticHypothesis with specified fields
class TherapeuticHypothesis(BaseModel):
    drug: str
    protein_target: str
    disease: str
    citation: str
    speakers: List[str]
    clinical_trial_names: List[str]
    results: List[str]
