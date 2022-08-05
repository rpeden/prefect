import pendulum
import pytest
from sqlalchemy import select

from prefect.orion import models
from prefect.orion.schemas.actions import FeatureFlagCreate
from prefect.orion.schemas.core import FeatureFlag

NOW = pendulum.now("UTC")


@pytest.fixture
def flag_data(client):
    yield [
        FeatureFlagCreate(
            name="a_flag",
        ),
        FeatureFlagCreate(
            name="b_flag",
        ),
    ]


@pytest.fixture
async def flags(flag_data, session):
    yield [
        await models.feature_flags.create_feature_flag(
            session=session, feature_flag=flag
        )
        for flag in flag_data
    ]


class TestCreateFeatureFlag:
    async def test_create_feature_flag_succeeds(self, session, flag_data, flags, db):
        query = select(db.FeatureFlag).order_by(db.FeatureFlag.name.asc())
        result = await session.execute(query)
        read_flags = result.scalars().unique().all()

        for i, flag in enumerate(read_flags):
            assert FeatureFlag.from_orm(flag) == flag_data[i]


class TestReadFeatureFlags:
    async def test_read_flags(self, session, flag_data, flags):
        read_flags = await models.feature_flags.read_feature_flags(session=session)
        assert len(read_flags) == 2

        for i, flag in enumerate(read_flags):
            assert FeatureFlag.from_orm(flag) == flag_data[i]
