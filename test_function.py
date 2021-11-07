import pytest
from utility import authenticate, find_user


@pytest.fixture
def clear_database():
    pass


def test_user_profiles():
    assert find_user('sampleUserN')
    assert find_user('other')
    assert find_user('random')
    assert (find_user('a'), False)
    assert authenticate('sampleUserN', 'samplePW')
    assert(authenticate('sampleUserN', 'a'), False)
    assert(authenticate('no', 'a'), False)
    assert(find_user('samplePW'), False)
    assert(find_user('thing'), False)
    assert(find_user('stuff'), False)