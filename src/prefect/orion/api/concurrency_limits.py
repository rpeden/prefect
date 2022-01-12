"""
Routes for interacting with concurrency limit objects.
"""

import datetime
from typing import List
from uuid import UUID

import pendulum
import sqlalchemy as sa
from fastapi import Body, Depends, HTTPException, Path, Response, status

from prefect import settings
from prefect.orion import models, schemas
from prefect.orion.api import dependencies
from prefect.orion.utilities.server import OrionRouter
from prefect.orion.database.dependencies import provide_database_interface
from prefect.orion.database.interface import OrionDBInterface

router = OrionRouter(prefix="/concurrency_limits", tags=["Concurrency Limits"])


@router.post("/")
async def create_concurrency_limit(
    concurrency_limit: schemas.actions.ConcurrencyLimitCreate,
    response: Response,
    session: sa.orm.Session = Depends(dependencies.get_session),
    db: OrionDBInterface = Depends(provide_database_interface),
) -> schemas.core.ConcurrencyLimit:

    # hydrate the input model into a full model
    deployment = schemas.core.ConcurrencyLimit(**concurrency_limit.dict())

    model = await models.concurrency_limits.create_concurrency_limit(
        session=session, concurrency_limit=concurrency_limit
    )

    if model.created >= pendulum.now():
        response.status_code = status.HTTP_201_CREATED

    return model


@router.get("/{id}")
async def read_concurrency_limit(
    concurrency_limit_id: UUID = Path(
        ..., description="The concurrency limit id", alias="id"
    ),
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> schemas.core.Deployment:
    """
    Get a concurrency limit by id.
    """
    model = await models.concurrency_limits.read_concurrency_limit(
        session=session, concurrency_limit_id=concurrency_limit_id
    )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )
    return model


@router.get("/tag/{tag}")
async def read_concurrency_limit_by_tag(
    tag: str = Path(..., description="The tag name", alias='tag'),
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> schemas.core.ConcurrencyLimit:
    """
    Get a deployment using the name of the flow and the deployment.
    """
    model = await models.concurrency_limits.read_concurrency_limit_by_tag(
        session=session, tag=tag
    )

    if not model:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )
    return model


@router.post("/filter")
async def read_concurrency_limits(
    limit: int = Body(
        settings.orion.api.default_limit, ge=0, le=settings.orion.api.default_limit
    ),
    offset: int = Body(0, ge=0),
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> List[schemas.core.ConcurrencyLimit]:
    """
    Query for concurrency limits.
    """

    return await models.concurrency_limits.read_concurrency_limits(
        session=session,
        limit=limit,
        offset=offset,
    )



@router.delete("/{id}")
async def delete_concurrency_limit(
    concurrency_limit_id: UUID = Path(
        ..., description="The concurrency limit id", alias="id"
    ),
    session: sa.orm.Session = Depends(dependencies.get_session),
):
    result = await models.concurrency_limits.delete_concurrency_limit(
        session=session, concurrency_limit_id=concurrency_limit_id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )


@router.delete("/tag/{tag}")
async def delete_concurrency_limit_by_tag(
    tag: str = Path(..., description="The tag name"),
    session: sa.orm.Session = Depends(dependencies.get_session),
):
    result = await models.concurrency_limits.delete_concurrency_limit_by_tag(
        session=session, tag=tag
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Concurrency limit not found"
        )
