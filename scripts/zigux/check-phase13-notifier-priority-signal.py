#!/usr/bin/env python3
"""Fail closed on the landed Phase 13 notifier priority-order convenience surface."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "PHASE13_NOTIFIER_PRIORITY_SIGNAL=pass"
SELF_TEST_CASE_COUNT = 5

FILE_SNIPPETS: dict[str, tuple[str, ...]] = {
    "zigux/bindings/notifier_abi.zig": (
        "pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",
        "pub const NotifierChainSummary",
    ),
    "zigux/helpers/notifier_chain_view.zig": (
        "pub fn hasNonincreasingPriorityOrder",
        "summarize keeps ordered terminated chains marked as nonincreasing priority",
        "summarize clears the priority-order flag when priorities rise",
    ),
    "include/zigux/notifier_abi.h": (
        "ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",
        "zigux_notifier_chain_has_nonincreasing_priority_order",
    ),
    "zigux/tests/phase13_notifier_list_reviewability.zig": (
        'expectContains(notifier_helper_text, "pub fn hasNonincreasingPriorityOrder")',
        'expectContains(exported_notifier_abi_text, "ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING")',
    ),
    "Documentation/zigux/phase13-notifier-list-survey.md": (
        "nonincreasing-priority signal",
        "check-phase13-notifier-priority-signal.py",
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def missing_snippets(path: Path, snippets: Iterable[str]) -> list[str]:
    text = read_text(path)
    return [snippet for snippet in snippets if snippet not in text]


def validate(repo_root: Path) -> None:
    missing_messages: list[str] = []
    for relative_path, snippets in FILE_SNIPPETS.items():
        path = repo_root / relative_path
        if not path.is_file():
            missing_messages.append(f"missing file: {relative_path}")
            continue
        missing = missing_snippets(path, snippets)
        if missing:
            missing_messages.extend(
                f"missing snippet in {relative_path}: {snippet}" for snippet in missing
            )

    if missing_messages:
        raise SystemExit("\n".join(missing_messages))

    print(PASS_MARKER)


def run_self_test() -> None:
    cases = [
        {"zigux/helpers/notifier_chain_view.zig": ("pub fn hasNonincreasingPriorityOrder",)},
        {"include/zigux/notifier_abi.h": ("zigux_notifier_chain_has_nonincreasing_priority_order",)},
        {"Documentation/zigux/phase13-notifier-list-survey.md": ("nonincreasing-priority signal",)},
        {"zigux/tests/phase13_notifier_list_reviewability.zig": ('expectContains(notifier_helper_text, "pub fn hasNonincreasingPriorityOrder")',)},
        {"zigux/bindings/notifier_abi.zig": ("pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",)},
    ]
    if len(cases) != SELF_TEST_CASE_COUNT:
        raise SystemExit(
            f"PHASE13_NOTIFIER_PRIORITY_SIGNAL_SELF_TEST_CASE_COUNT={len(cases)} expected={SELF_TEST_CASE_COUNT}"
        )
    print(
        f"PHASE13_NOTIFIER_PRIORITY_SIGNAL_SELF_TEST=pass cases={SELF_TEST_CASE_COUNT}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    validate(REPO_ROOT)


if __name__ == "__main__":
    main()
