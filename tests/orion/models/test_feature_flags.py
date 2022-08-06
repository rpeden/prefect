import pendulum
import pytest
from sqlalchemy import select

from prefect.orion import models
from prefect.orion.schemas.actions import FeatureFlagCreate, FeatureFlagUpdate
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
async def feature_flags(flag_data, session, db):
    for flag in flag_data:
        await models.feature_flags.create_feature_flag(
            session=session, feature_flag=flag
        )
    query = select(db.FeatureFlag).order_by(db.FeatureFlag.name.asc())
    result = await session.execute(query)
    return result.scalars().unique().all()


class TestCreateFeatureFlag:
    async def test_create_feature_flag_succeeds(
        self, session, flag_data, feature_flags, db
    ):
        query = select(db.FeatureFlag).order_by(db.FeatureFlag.name.asc())
        result = await session.execute(query)
        read_flags = result.scalars().unique().all()

        for i, flag in enumerate(read_flags):
            assert FeatureFlag.from_orm(flag) == flag_data[i]


class TestReadFeatureFlags:
    async def test_read_flags(self, session, flag_data, feature_flags):
        read_flags = await models.feature_flags.read_feature_flags(session=session)
        assert len(read_flags) == 2

        for i, flag in enumerate(read_flags):
            assert FeatureFlag.from_orm(flag) == flag_data[i]


class TestReadFeatureFlag:
    async def test_read_flag(self, session, flag_data, feature_flags):
        retrieved_flag = await models.feature_flags.read_feature_flag(
            session, feature_flags[0].id
        )
        assert FeatureFlag.from_orm(retrieved_flag) == flag_data[0]


class TestUpdateFeatureFlag:
    async def test_update_flag(self, session, flag_data, feature_flags, db):
        flag = feature_flags[0]
        updated_flag_schema = FeatureFlagUpdate.from_orm(flag)
        updated_flag_schema.name = "new flag name"

        successful = await models.feature_flags.update_feature_flag(
            session=session, feature_flag_id=flag.id, feature_flag=updated_flag_schema
        )
        assert successful is True

        retrieved_updated_flag = await session.get(db.FeatureFlag, flag.id)
        assert retrieved_updated_flag.name == "new flag name"
