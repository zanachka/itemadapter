import unittest
from unittest import mock

import scrapy

from itemadapter.utils import is_item, is_attrs_instance, is_dataclass_instance, is_scrapy_item

from tests import AttrsItem, DataClassItem, ScrapyItem, ScrapySubclassedItem


def mocked_import(name, *args, **kwargs):
    raise ImportError(name)


class ItemLikeTestCase(unittest.TestCase):
    def test_false(self):
        self.assertFalse(is_item(int))
        self.assertFalse(is_item(sum))
        self.assertFalse(is_item(1234))
        self.assertFalse(is_item(object()))
        self.assertFalse(is_item("a string"))
        self.assertFalse(is_item(b"some bytes"))
        self.assertFalse(is_item(["a", "list"]))
        self.assertFalse(is_item(("a", "tuple")))
        self.assertFalse(is_item({"a", "set"}))
        self.assertFalse(is_item(dict))
        self.assertFalse(is_item(ScrapyItem))
        self.assertFalse(is_item(DataClassItem))
        self.assertFalse(is_item(ScrapySubclassedItem))
        self.assertFalse(is_item(AttrsItem))

    def test_true(self):
        self.assertTrue(is_item({"a": "dict"}))
        self.assertTrue(is_item(ScrapyItem()))
        self.assertTrue(is_item(ScrapySubclassedItem(name="asdf", value=1234)))
        self.assertTrue(is_item(AttrsItem(name="asdf", value=1234)))

    @unittest.skipIf(not DataClassItem, "dataclasses module is not available")
    def test_dataclass(self):
        self.assertTrue(is_item(DataClassItem(name="asdf", value=1234)))


class AttrsTestCase(unittest.TestCase):
    def test_false(self):
        self.assertFalse(is_attrs_instance(int))
        self.assertFalse(is_attrs_instance(sum))
        self.assertFalse(is_attrs_instance(1234))
        self.assertFalse(is_attrs_instance(object()))
        self.assertFalse(is_attrs_instance(ScrapyItem()))
        self.assertFalse(is_attrs_instance(ScrapySubclassedItem()))
        self.assertFalse(is_attrs_instance("a string"))
        self.assertFalse(is_attrs_instance(b"some bytes"))
        self.assertFalse(is_attrs_instance({"a": "dict"}))
        self.assertFalse(is_attrs_instance(["a", "list"]))
        self.assertFalse(is_attrs_instance(("a", "tuple")))
        self.assertFalse(is_attrs_instance({"a", "set"}))

    @mock.patch("builtins.__import__", mocked_import)
    def test_module_not_available(self):
        self.assertFalse(is_attrs_instance(AttrsItem(name="asdf", value=1234)))

    def test_true(self):
        self.assertTrue(is_attrs_instance(AttrsItem()))
        self.assertTrue(is_attrs_instance(AttrsItem(name="asdf", value=1234)))


class DataclassTestCase(unittest.TestCase):
    def test_false_always(self):
        """These objects should return False whether or not the dataclasses module is available"""
        self.assertFalse(is_dataclass_instance(int))
        self.assertFalse(is_dataclass_instance(sum))
        self.assertFalse(is_dataclass_instance(1234))
        self.assertFalse(is_dataclass_instance(object()))
        self.assertFalse(is_dataclass_instance(ScrapyItem()))
        self.assertFalse(is_dataclass_instance(AttrsItem()))
        self.assertFalse(is_dataclass_instance(ScrapySubclassedItem()))
        self.assertFalse(is_dataclass_instance("a string"))
        self.assertFalse(is_dataclass_instance(b"some bytes"))
        self.assertFalse(is_dataclass_instance({"a": "dict"}))
        self.assertFalse(is_dataclass_instance(["a", "list"]))
        self.assertFalse(is_dataclass_instance(("a", "tuple")))
        self.assertFalse(is_dataclass_instance({"a", "set"}))

    @unittest.skipIf(not DataClassItem, "dataclasses module is not available")
    @mock.patch("builtins.__import__", mocked_import)
    def test_module_not_available(self):
        self.assertFalse(is_dataclass_instance(DataClassItem(name="asdf", value=1234)))

    @unittest.skipIf(not DataClassItem, "dataclasses module is not available")
    def test_false_only_if_installed(self):
        self.assertFalse(is_dataclass_instance(DataClassItem))

    @unittest.skipIf(not DataClassItem, "dataclasses module is not available")
    def test_true_only_if_installed(self):
        self.assertTrue(is_dataclass_instance(DataClassItem()))
        self.assertTrue(is_dataclass_instance(DataClassItem(name="asdf", value=1234)))


class ScrapyItemTestCase(unittest.TestCase):
    def test_false(self):
        self.assertFalse(is_scrapy_item(int))
        self.assertFalse(is_scrapy_item(sum))
        self.assertFalse(is_scrapy_item(1234))
        self.assertFalse(is_scrapy_item(object()))
        self.assertFalse(is_scrapy_item(AttrsItem()))
        self.assertFalse(is_scrapy_item("a string"))
        self.assertFalse(is_scrapy_item(b"some bytes"))
        self.assertFalse(is_scrapy_item({"a": "dict"}))
        self.assertFalse(is_scrapy_item(["a", "list"]))
        self.assertFalse(is_scrapy_item(("a", "tuple")))
        self.assertFalse(is_scrapy_item({"a", "set"}))
        self.assertFalse(is_scrapy_item(ScrapySubclassedItem))

    @mock.patch("builtins.__import__", mocked_import)
    def test_module_not_available(self):
        self.assertFalse(is_scrapy_item(ScrapySubclassedItem(name="asdf", value=1234)))

    def test_true_only(self):
        self.assertTrue(is_scrapy_item(ScrapySubclassedItem()))
        self.assertTrue(is_scrapy_item(ScrapyItem()))
        self.assertTrue(is_scrapy_item(ScrapySubclassedItem(name="asdf", value=1234)))


class ScrapyDeprecatedBaseItemTestCase(unittest.TestCase):
    @unittest.skipIf(not hasattr(scrapy.item, "_BaseItem"), "scrapy.item._BaseItem not available")
    def test_deprecated_underscore_baseitem(self):
        class SubClassed_BaseItem(scrapy.item._BaseItem):
            pass

        self.assertTrue(is_scrapy_item(scrapy.item._BaseItem()))
        self.assertTrue(is_scrapy_item(SubClassed_BaseItem()))

    @unittest.skipIf(not hasattr(scrapy.item, "BaseItem"), "scrapy.item.BaseItem not available")
    def test_deprecated_baseitem(self):
        class SubClassedBaseItem(scrapy.item.BaseItem):
            pass

        self.assertTrue(is_scrapy_item(scrapy.item.BaseItem()))
        self.assertTrue(is_scrapy_item(SubClassedBaseItem()))

    def test_removed_baseitem(self):
        class MockItemModule:
            Item = ScrapyItem

        with mock.patch("scrapy.item", MockItemModule):
            self.assertFalse(is_scrapy_item(dict()))
            self.assertFalse(is_scrapy_item(AttrsItem()))
