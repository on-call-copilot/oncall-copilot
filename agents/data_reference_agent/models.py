from typing import List
from pydantic import BaseModel, Field


class DataModel(BaseModel):
    model: str = Field(description="Name of the data model.")
    fields: List[str] = Field(description="List of relevant fields within the data model.")


class DataModelList(BaseModel):
    data_models: List[DataModel] = Field(description="List of data models.")


class GetDataModelsInput(BaseModel):
    ticket_description: str = Field(
        description="The description from the JIRA ticket, detailing the issue."
    )