from fastapi import APIRouter, Depends, Request
from src.api import auth
from enum import Enum

from datetime import datetime


import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/search",
    tags=["search"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    track = "track"
    album = "album"
    artist = "artist"
    genre = "genre"
    
@router.get("/")
def search_tracks(
    track: str = "",
    artist: str = "",
    album: str = "",
):
    results = []
    # Use reflection to derive table schema.
    metadata_obj = sqlalchemy.MetaData()
    tracks = sqlalchemy.Table("tracks", metadata_obj, autoload_with=db.engine)
        
    stmt = (
        sqlalchemy.select(
            tracks.c.id,
            tracks.c.track_name,
            tracks.c.album_name, 
            tracks.c.artists
        )
    )
    
    if track != "":
        stmt = stmt.where(tracks.c.track_name.ilike(f"%{track}%"))
    
    if album != "":
        stmt = stmt.where(tracks.c.album_name.ilike(f"%{album}%"))
    
    if artist != "":
        stmt = stmt.where(tracks.c.artists.ilike(f"%{artist}%"))
        
    with db.engine.begin() as connection:
        result = connection.execute(stmt)

        for row in result:
            results.append({
                "id": row.id,
                "track": row.track_name,
                "album": row.album_name,
                "artist": row.artists,
            })
    
    return {
        "results": results,
    }
    
        
    