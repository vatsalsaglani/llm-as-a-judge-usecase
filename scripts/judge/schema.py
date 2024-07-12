from pydantic import BaseModel, Field
## judge output schema


class JudgeOutput(BaseModel):
    evaluation: str = Field(
        ...,
        description=
        "Your rationale for the rating, explaining how well the function call aligns with the user's request"
    )
    rating: int = Field(
        ...,
        description="Your rating, as a number between 1 and 4.",
        ge=1,
        le=4)


judge_functions = [{
    "name": "JudgeSystemGeneratedResponse",
    "description":
    "Provide your score for the system generated output in context of the user messages",
    "parameters": JudgeOutput.model_json_schema()
}]
