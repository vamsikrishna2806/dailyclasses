from pydantic import BaseModel, field_validator, model_validator

class SignUp(BaseModel):
    username: str
    password: str
    confirm: str

    @field_validator("username")
    @classmethod
    def no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("username cannot contain spaces")
        return v.lower()                  # you can also clean the value

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm:
            raise ValueError("passwords do not match")
        return self
