from pydantic import BaseModel


class InstitutionView(BaseModel):
    id: str
    name: str
    region: str
    is_new: bool
    version: int


class InstitutionPage(BaseModel):
    items: list[InstitutionView]
    total: int
    limit: int
    offset: int
