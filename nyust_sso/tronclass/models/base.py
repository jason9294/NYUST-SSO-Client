from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseResourceModel(BaseModel):
    raw_data: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self.raw_data = data

    model_config = ConfigDict(extra="allow")  # 允許額外的欄位
