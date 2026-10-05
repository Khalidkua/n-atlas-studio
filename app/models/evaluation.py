from pydantic import BaseModel, Field


class EvaluationExample(BaseModel):
    id: str
    language: str
    domain: str
    task_type: str = "question_answering"
    prompt: str
    reference_answer: str


class EvaluationDataset(BaseModel):
    name: str
    examples: list[EvaluationExample] = Field(default_factory=list)
