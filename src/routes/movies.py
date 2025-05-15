from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_

from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models.movies import (
    Movie,
    Genre,
    Director,
    Star,
)

from src.schemas.movies import (
    MovieListItemSchema,
    MovieListResponseSchema,
)

router = APIRouter()


@router.get(
    "/",
    response_model=MovieListResponseSchema,
    summary="Get a paginated list of movies",
    description=(
        "This endpoint retrieves a paginated list of movies from the database. "
        "Clients can specify the `page` number and the number of items per page using `per_page`. "
        "The response includes details about the movies, total pages, and total items, "
        "along with links to the previous and next pages if applicable."
    ),
    responses={
        404: {
            "description": "No movies found.",
            "content": {
                "application/json": {"example": {"detail": "No movies found."}}
            },
        }
    },
)
def get_movie_list(
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
    year: int | None = Query(None, description="Filter by year"),
    min_imdb: float | None = Query(None, description="Filter by min_imdb"),
    max_imdb: float | None = Query(None, description="Filter by max_imdb"),
    genre: str | None = Query(None, description="Filter by genre name"),
    director: str | None = Query(None, description="Filter by director name"),
    star: str | None = Query(None, description="Filter by star name"),
    search: str | None = Query(
        None, description="Search by title, description, actor or director"
    ),
    sort_by: str | None = Query(None, description="Sort by 'price', 'year', 'votes'"),
    db: Session = Depends(get_db),
) -> MovieListResponseSchema:
    """
    Fetch a paginated list of movies from the database.

    This function retrieves a paginated list of movies, allowing the client to specify
    the page number and the number of items per page. It calculates the total pages
    and provides links to the previous and next pages when applicable.
    """
    offset = (page - 1) * per_page

    query = db.query(Movie).order_by()

    order_by = Movie.default_order_by()
    if order_by:
        query = query.order_by(*order_by)

    if year:
        query = query.filter(Movie.year == year)
    if min_imdb:
        query = query.filter(Movie.imdb >= min_imdb)
    if max_imdb:
        query = query.filter(Movie.imdb <= max_imdb)
    if director:
        query = query.join(Movie.directors).filter(Director.name.ilike(f"%{director}%"))
    if star:
        query = query.join(Movie.stars).filter(Star.name.ilike(f"%{star}%"))
    if genre:
        query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre}%"))

    if search:
        query = (
            query.outerjoin(Movie.directors)
            .outerjoin(Movie.stars)
            .filter(
                or_(
                    Movie.name.ilike(f"%{search}%"),
                    Movie.description.ilike(f"%{search}%"),
                    Director.name.ilike(f"%{search}%"),
                    Star.name.ilike(f"%{search}%"),
                )
            )
        )

    sort_fields = {
        "price": Movie.price,
        "year": Movie.year,
        "votes": Movie.votes,
    }
    if sort_by in sort_fields:
        query = query.order_by(sort_fields[sort_by].desc())

    total_items = query.count()

    movies = query.offset(offset).limit(per_page).all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    movie_list = [MovieListItemSchema.model_validate(movie) for movie in movies]

    total_pages = (total_items + per_page - 1) // per_page

    response = MovieListResponseSchema(
        movies=movie_list,
        prev_page=f"/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        next_page=(
            f"/movies/?page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        ),
        total_pages=total_pages,
        total_items=total_items,
    )
    return response
