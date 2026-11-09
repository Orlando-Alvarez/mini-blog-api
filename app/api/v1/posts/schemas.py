from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional, List, Literal


class Tag(BaseModel):
    name: str = Field(min_length=2, max_length=20, description="Nombre de la etiqueta")
    
    model_config = ConfigDict(from_attributes=True)
    
class Author(BaseModel):
    name: str
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None
    
    model_config = ConfigDict(from_attributes=True)
    
class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        examples=["Titulo"],
        description= "Titulo"
    )
    content: Optional[str] = Field(
        default= "Este es un contenido por defecto",
        min_length= 10,
        max_length= 100,
        examples= ["Contenido"],
        description="Contenido"
    )
    tags: List[Tag] = Field(examples= ['[{"name":"FastAPI"}]'])
    # author: Optional[Author] = None

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None

class PostPublic(PostBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class PostSummary(BaseModel):
    id: int
    title: str
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal ["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]
