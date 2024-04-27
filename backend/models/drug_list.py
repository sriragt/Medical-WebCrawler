from pydantic import BaseModel, Field
from typing import List

# Pydantic model for DrugList with specified fields
class DrugList(BaseModel):
    drugs: List[str] = Field(..., description="A list of drugs that are described in excerpt. If not directly named, use best effort for the most appropriate names.")
