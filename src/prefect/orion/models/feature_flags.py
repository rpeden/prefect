"""
Functions for interacting with feature flag ORM objects.
Intended for internal use by the Orion API.
"""

import sqlalchemy as sa
from sqlalchemy import select

import prefect.orion.schemas as schemas
from prefect.orion.database.dependencies import inject_db
from prefect.orion.database.interface import OrionDBInterface


@inject_db
async def create_feature_flag(
    session: sa.orm.Session,
    db: OrionDBInterface,
    feature_flag: schemas.core.FeatureFlag,
):
    """
    Creates a new feature flag.

    Args:
        session: a database session
        feature_flag: a feature flag schema

    Returns:
        db.FeatureFlag: the newly-created feature flag
    """
    flag_insert = await db.insert(db.FeatureFlag)
    await session.execute(flag_insert.values(**feature_flag.dict()))


@inject_db
async def read_feature_flags(
    session: sa.orm.Session,
    db: OrionDBInterface,
):
    """
    Read feature flags.

    Args:
        session: a database session
        db: the database interface

    Returns:
        List[db.FeatureFlag]: the matching feature flags
    """
    query = select(db.FeatureFlag).order_by(db.FeatureFlag.name.asc())
    result = await session.execute(query)
    return result.scalars().unique().all()
