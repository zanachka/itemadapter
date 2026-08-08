import unittest

from itemadapter.adapter import DictAdapter, ItemAdapter
from tests import DataClassItem


class DictOnlyItemAdapter(ItemAdapter):
    ADAPTER_CLASSES = [DictAdapter]


class ItemAdapterTestCase(unittest.TestCase):
    def test_repr(self):
        adapter = ItemAdapter({"foo": "bar"})
        assert repr(adapter) == "<ItemAdapter for dict(foo='bar')>"

    def test_adapter_classes_change(self):
        item = DataClassItem()
        adapter_classes = ItemAdapter.ADAPTER_CLASSES
        assert ItemAdapter.is_item(item)
        ItemAdapter.ADAPTER_CLASSES = (DictAdapter,)
        try:
            assert not ItemAdapter.is_item(item)
        finally:
            ItemAdapter.ADAPTER_CLASSES = adapter_classes
        assert ItemAdapter.is_item(item)

    def test_repr_subclass(self):
        adapter = DictOnlyItemAdapter({"foo": "bar"})
        assert repr(adapter) == "<DictOnlyItemAdapter for dict(foo='bar')>"
