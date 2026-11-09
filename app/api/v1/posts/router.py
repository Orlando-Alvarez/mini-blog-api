
from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from math import ceil
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Literal, Optional, List,  Union
from app.core.db import get_db
from .schemas import (PostPublic, PostCreate, PostSummary, PostUpdate, PaginatedPost)
from .repository import PostRepository
from app.core.security import oauth2_scheme, get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("", response_model=PaginatedPost)
def list_posts(
    text : Optional[str] = Query(
    default = None,
    deprecated=True,
    description = "Parametros obsoletos, usar 'Query' o 'Search' en su lugar."
),
    query : Optional[str] = Query(
    default = None,
    description = "Buscar por titulo",
    alias = "Search",
    min_length= 3,
    max_length= 50,
),
    per_page: int = Query(
    10,
    ge = 1,
    le = 50,
    description = "Numero de resultados (1-50)"
),
    page: int = Query(
    1,
    ge = 1,
    description= "Numero de Pagina(>=1)"
),
    order_by: Literal["id", "title"] = Query(
        "id", 
        description= "Campo de orden"
),
    direction: Literal["asc", "desc"] = Query(
        "asc",
        description= "direccion de orden (ascendente)"
),
    db: Session = Depends(get_db)
):
    repository = PostRepository(db)
    query = query or text
    
    total, items = repository.search(
        query=query,
        order_by=order_by,
        direction=direction,
        page=page,
        per_page=per_page,
    )
    
    total_pages = ceil(total/per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)
    
    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False
    
    return PaginatedPost(
        total=total,
        total_pages=total_pages,
        page=page,
        per_page=per_page,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )

@router.get("/by-tags", response_model= List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description= "Una o mas etiquetas. Ejemplo: ?tags=python&tags=fastapi"
    ),
    db: Session = Depends(get_db)
):
    repository = PostRepository(db)
    return repository.by_tags(tags)

@router.get("/{post_id}", response_model=Union[PostPublic, PostSummary], response_description= "Post encontrado" )
def get_post(post_id : int = Path(
    ...,
    ge=1,
    title="ID del Post",
    description="ID debe ser mayor a 1",
    example=1
    ), include_content : bool | None = Query(default = True, description = "Activar o desactivar contenido"), db: Session= Depends(get_db)):
    
    repository = PostRepository(db)
    post = repository.get(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)
    
    return PostSummary.model_validate(post, from_attributes=True)

@router.post("", response_model = PostPublic, response_description = "Post creado exitosamente!!", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), user= Depends(get_current_user)):
    repository = PostRepository(db)
    try:
        post = repository.create_post(
            title = post.title,
            content= post.content,
            author= user,
            tags= [tag.model_dump() for tag in post.tags]
        )
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El titulo ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")

@router.put("/{post_id}", response_model=PostPublic, response_description= "Post Actualizado exitosamente!!", response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db), user= Depends(get_current_user)):
    
    repository = PostRepository(db)
    post = repository.get(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    try:
        updates = data.model_dump(exclude_unset=True)
        post = repository.update_post(post, updates)
        db.commit()
        db.refresh(post)
        return post
    except SQLAlchemyError:
         db.rollback()
         raise HTTPException(status_code=500, detail="Error al actualizar Post")

@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), user= Depends(get_current_user)):
    repository = PostRepository(db)
    post = repository.get(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    try:
        repository.delete_post(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="No se pudo borrar el post")

@router.get("/secure")
def secure_endpoint(token: str = Depends(oauth2_scheme)):
    return {"message": "Acceso con token", "token_recibifo": token}
