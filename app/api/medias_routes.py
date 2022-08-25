from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request
from fastapi.responses import FileResponse
from crud import media_crud
from schemas import media_schema
from repository import media_repository
from db.database import get_db
from typing import List
from utils.status import Status, get_responses
from utils import merger
import exceptions.CustomException
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/medias/output/{filename}", tags=["Medias"], description="Get merged image")
async def get_merged_image(filename: str, request: Request, db: Session = Depends(get_db)):
    return FileResponse(f"medias/output/{filename}")


@router.post("/medias/merge", responses=get_responses([200, 404, 500]), tags=["Medias"], description="Generate image")
def generate_image(media_ids: List[str], request: Request, db: Session = Depends(get_db)):

    rawListImages = []

    for media_id in media_ids:
        db_media = media_crud.get_media(db=db, id=media_id)
        if db_media is None:
            raise exceptions.CustomException.CustomException(
                db=db,
                status_code=404,
                detail="Media not found",
                info=f"Media {media_id} not found"
            )
        rawListImages.append(merger.get_image_from_url(db_media.content_url))

    # Generate image
    image_name = merger.merge_image_list(rawListImages)
    return JSONResponse(
        status_code=200,
        content={"filename": image_name}
    )


@router.delete("/medias/{media_id}", responses=get_responses([204, 404, 500]), tags=["Medias"], description="Delete media")
def delete_media(media_id: int, request: Request, db: Session = Depends(get_db)):

    db_media = media_crud.get_media(db=db, id=media_id)
    if db_media is None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="Media not found",
            info=f"Media {media_id} not found"
        )
    try:
        media_repository.delete_media(db=db, db_media=db_media)
        return Status(detail=f"Media {media_id} successfully deleted")
    except Exception as e:
        print(str(e))
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=500,
            detail=f"Internal error while trying to delete media {media_id}",
            info=f"Internal error while trying to delete media {media_id}",
        )


@router.get("/medias/{media_id}", response_model=media_schema.MediaResponse, responses=get_responses([204, 404, 500]), tags=["Medias"], description="Delete media")
def get_media(media_id: int, request: Request, db: Session = Depends(get_db)):

    db_media = media_crud.get_media(db=db, id=media_id)
    if db_media is None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="Media not found",
            info=f"Media {media_id} not found"
        )
    return db_media
