from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class BaseResourceModel(BaseModel):
    _raw_data: dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self._raw_data = data

    model_config = ConfigDict(extra="allow")  # 允許額外的欄位
