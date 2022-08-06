"""
Functions for interacting with feature flag ORM objects.
Intended for internal use by the Orion API.
"""
from uuid import UUID

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
        None
    """
    flag_insert = await db.insert(db.FeatureFlag)
    await session.execute(flag_insert.values(**feature_flag.dict()))


@inject_db
async def read_feature_flag(
    session: sa.orm.Session, feature_flag_id: UUID, db: OrionDBInterface
):
    """
    Reads a feature flag by ID.

    Args:
        session: A database session
        feature_flag_id: a feature flag ID

    Returns:
        db.FeatureFlag: the feature flag
    """

    return await session.get(db.FeatureFlag, feature_flag_id)


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


@inject_db
async def update_feature_flag(
    session: sa.orm.Session,
    feature_flag_id: UUID,
    feature_flag: schemas.actions.FeatureFlagUpdate,
    db: OrionDBInterface,
) -> bool:
    """
    Updates a feature flag.

    Args:
        session: a database session
        feature_flag_id: the feature flag id to update
        feature_flag: a feature flag model

    Returns:
        bool: whether or not matching rows were found to update
    """
    update_stmt = (
        sa.update(db.FeatureFlag).where(db.FeatureFlag.id == feature_flag_id)
        # exclude_unset=True allows us to only update values provided by
        # the user, ignoring any defaults on the model
        .values(**feature_flag.dict(shallow=True, exclude_unset=True))
    )
    result = await session.execute(update_stmt)
    return result.rowcount > 0
