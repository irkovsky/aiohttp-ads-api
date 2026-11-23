from typing import Optional
import pydantic
from errors import HttpError

class CreateUser(pydantic.BaseModel):
    email: str
    password: str

class CreateAd(pydantic.BaseModel):
    title: str
    description: Optional[str] = None

class UpdateAd(pydantic.BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    
def validate(schema_class, json_data):
    try:
        return schema_class(**json_data).model_dump(exclude_unset=True)
    except pydantic.ValidationError as err:
        error = err.errors()[0]
        error.pop("ctx", None)
        raise HttpError(400, error)