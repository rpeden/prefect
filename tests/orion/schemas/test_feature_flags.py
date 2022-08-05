import pytest
from pydantic import ValidationError

from prefect.orion.schemas.actions import FeatureFlagCreate
from prefect.orion.schemas.core import FeatureFlag


def test_feature_flag_name_is_required():
    with pytest.raises(ValidationError, match="field required"):
        FeatureFlag()


def test_feature_flag_accepts_json_data():
    flag = FeatureFlagCreate(name="feature", data={"field": True})
    assert flag.json() == '{"name": "feature", "data": {"field": true}}'


def test_feature_flag_rejects_non_dict_data():
    with pytest.raises(ValidationError, match="value is not a valid dict"):
        FeatureFlagCreate(name="feature", data=False)


def test_feature_flag_rejects_non_json_raw_data():
    with pytest.raises(ValidationError, match="value is not a valid dict"):
        FeatureFlagCreate.parse_raw('{"name": "test", "data":true}')
