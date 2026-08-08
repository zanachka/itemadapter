import pytest

from itemadapter.adapter import _find_adapter_class


@pytest.fixture(autouse=True)
def _clear_adapter_class_cache():
    """Keep tests that change which item types are supported, e.g. by patching
    an optional import out, from seeing results cached by earlier tests."""
    _find_adapter_class.cache_clear()
