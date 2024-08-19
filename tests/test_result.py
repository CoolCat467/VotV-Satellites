"""Test vector module."""

from __future__ import annotations

from votv_satellites.result import Result


def test_result_ok() -> None:
    result = Result.ok("yas")
    assert result.success
    assert result.value == "yas"


def test_result_fail() -> None:
    result = Result.fail("failure text")
    assert not result.success
    assert result.value == "failure text"


def test_result_success_bool() -> None:
    result = Result.ok("yas 2")
    assert result
    assert result.value == "yas 2"


def test_result_failure_bool() -> None:
    result = Result.fail("failures 2")
    assert not result
    assert result.value == "failures 2"


def test_result_success_unwrap() -> None:
    result = Result.ok("success string")
    assert result.unwrap() == "success string"


def test_result_fail_unwrap() -> None:
    result = Result.fail("failure string")
    assert result.unwrap() == "failure string"
