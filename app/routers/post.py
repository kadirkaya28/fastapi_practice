from typing import Optional

from fastapi import status, HTTPException, APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import func

from ..database import get_db
from fastapi.params import Depends
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10,
              skip: int = 0, q: Optional[str] = ""):
    #     cursor.execute("select * from posts")
    #     posts = cursor.fetchall()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).\
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).\
        filter(models.Post.title.contains(q)).limit(limit).offset(skip).all()
    return posts


@router.get("/latest", response_model=schemas.PostOut)
def get_latest_post(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC""")
    # latest_post = cursor.fetchone()
    latest_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")). \
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id). \
        order_by(models.Post.created_at.desc()).first()

    return latest_post


# bu 2 rootun sıralaması çok önemli eğer id li olanı yukarı taşırsak latest a asla erişemiyoruz !!!
# posts/ dan sonrakileri id olarak algılıyor ve sürekli bad type hatası dönüyor !!!!

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = ? """, (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).\
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id). \
        filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with id: {id} was not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(payload: schemas.Post, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published)
    #                     VALUES (?, ?, ?)
    #                     RETURNING *""", (payload.title, payload.content, payload.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id=current_user.id, **payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", response_model=schemas.PostResponse)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts WHERE id = ? RETURNING * """, (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id == id).first()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with id: {id} does not exist")

    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action.")
    db.delete(deleted_post)
    db.commit()
    return deleted_post


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, payload: schemas.Post, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE posts
    #                     SET title = ?, content= ?, published = ?
    #                     WHERE id = ?
    #                     RETURNING * """, (payload.title, payload.content, payload.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    updated_post = db.query(models.Post).filter(models.Post.id == id)
    if not updated_post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with id: {id} was not found")
    if updated_post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action.")

    updated_post.update(values=payload.dict(), synchronize_session=False)
    db.commit()
    return updated_post.first()
