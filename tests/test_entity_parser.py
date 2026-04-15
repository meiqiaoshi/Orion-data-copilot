from __future__ import annotations

from app.entity_parser import parse_config_path, parse_dataset_name, parse_pipeline_name


def test_parse_pipeline_equals_form() -> None:
    assert parse_pipeline_name("pipeline=orders failed") == "orders"


def test_parse_pipeline_chinese() -> None:
    assert parse_pipeline_name("管道 orders 失败了") == "orders"


def test_parse_dataset_equals_form() -> None:
    assert parse_dataset_name("dataset=raw_orders alerts") == "raw_orders"


def test_parse_dataset_chinese() -> None:
    assert parse_dataset_name("数据集 raw_orders 有问题") == "raw_orders"


def test_parse_config_explicit_prefix() -> None:
    assert parse_config_path("run config=configs/foo.yaml now") == "configs/foo.yaml"
