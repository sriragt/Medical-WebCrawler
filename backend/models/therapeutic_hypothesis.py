from pydantic import BaseModel, Field
from typing import List

# Pydantic model for TherapeuticHypothesis with specified fields
class TherapeuticHypothesis(BaseModel):
    drug: str = Field(..., description="The name of the drug. If not directly named, use best effort for the most appropriate name.")
    protein_target: str = Field(..., description="The protein target that the drug hits, if it is mentioned in the excerpt. Otherwise, write \"not mentioned\".")
    disease: str = Field(..., description="The disease that the drug addresses, if it is mentioned in the excerpt. Otherwise, write \"not mentioned\".")
    citation: str = Field(..., description="Verbatim text that supports the extracted claims. Write \"not mentioned\" if not found.")
    speakers: List[str] = Field(..., description="The speakers who are making the extracted claims. Write \"not mentioned\" if not found.")
    clinical_trial_names: List[str] = Field(..., description="The name of any past or upcoming clinical trials that will feature this drug. Write \"not mentioned\" if not found.")
    results: List[str] = Field(..., description="The results (e.g., overall survival, progression-free survival). Be concise. Write \"not mentioned\" if not found.")

    # Convert TherapeuticHypothesis object to a dictionary.
    def to_dict(self) -> dict:
        return {
            "drug": self.drug,
            "protein_target": self.protein_target,
            "disease": self.disease,
            "citation": self.citation,
            "speakers": self.speakers,
            "clinical_trial_names": self.clinical_trial_names,
            "results": self.results
        }