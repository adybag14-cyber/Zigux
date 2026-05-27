#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIRECT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
ROUTE = "make -C zigux phase2-cross"

DIRECT_CHECKER_MARKERS = (
    'EXPECTED_SELF_TEST_CASE_COUNT = 17',
    '"target": "riscv64-linux"',
    '"review_status": "route contract only"',
    '"validation_mode": "route_contract_only"',
)

ALIGNMENT_MARKERS = (
    'SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux", "riscv64-linux")',
    '"target": "riscv64-linux"',
    '"review_status": "route contract only"',
    '"validation_mode": "route_contract_only"',
)

EXPECTED_FIXTURE = {
    "phase": "Phase 2",
    "status": "active",
    "route": ROUTE,
    "archive_target_scope": ["x86_64-linux"],
    "cross_targets": [
        {
            "target": "x86_64-linux",
            "review_status": "pinned bootstrap archive",
            "validation_mode": "archive_required",
            "route": ROUTE,
        },
        {
            "target": "aarch64-linux",
            "review_status": "route contract only",
            "validation_mode": "route_contract_only",
            "route": ROUTE,
        },
        {
            "target": "riscv64-linux",
            "review_status": "route contract only",
            "validation_mode": "route_contract_only",
            "route": ROUTE,
        },
    ],
}

EXPECTED_SELF_TEST_CASE_COUNT = 8


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_marker_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_fixture_issues(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]

    issues: list[tuple[str, str]] = []
    for key in ("phase", "status", "route", "archive_target_scope", "cross_targets"):
        if payload.get(key) != EXPECTED_FIXTURE[key]:
            issues.append(("INVALID_FIXTURE_FIELD", key))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    direct_checker = read_text(resolve_path(root, DIRECT_CHECKER))
    alignment_checker = read_text(resolve_path(root, ALIGNMENT_CHECKER))
    fixture = read_json(resolve_path(root, FIXTURE))

    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_marker_issues(
            direct_checker,
            DIRECT_CHECKER_MARKERS,
            "MISSING_DIRECT_CHECKER_MARKER",
        )
    )
    issues.extend(
        collect_marker_issues(
            alignment_checker,
            ALIGNMENT_MARKERS,
            "MISSING_ALIGNMENT_MARKER",
        )
    )
    issues.extend(collect_fixture_issues(fixture))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_THREE_TARGET_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        resolve_path(root, DIRECT_CHECKER),
        "\n".join(
            (
                "EXPECTED_SELF_TEST_CASE_COUNT = 17",
                '"target": "riscv64-linux"',
                '"review_status": "route contract only"',
                '"validation_mode": "route_contract_only"',
            )
        )
        + "\n",
    )
    write_text(
        resolve_path(root, ALIGNMENT_CHECKER),
        "\n".join(
            (
                'SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux", "riscv64-linux")',
                '"target": "riscv64-linux"',
                '"review_status": "route contract only"',
                '"validation_mode": "route_contract_only"',
            )
        )
        + "\n",
    )
    write_text(resolve_path(root, FIXTURE), json.dumps(EXPECTED_FIXTURE, indent=2) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_three_target_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        direct_path = resolve_path(root, DIRECT_CHECKER)
        direct_path.write_text(
            direct_path.read_text(encoding="utf-8").replace(DIRECT_CHECKER_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        assert ("MISSING_DIRECT_CHECKER_MARKER", DIRECT_CHECKER_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        alignment_path = resolve_path(root, ALIGNMENT_CHECKER)
        alignment_path.write_text(
            alignment_path.read_text(encoding="utf-8").replace(ALIGNMENT_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        assert ("MISSING_ALIGNMENT_MARKER", ALIGNMENT_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"].pop()
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "cross_targets") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][2]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "cross_targets") in collect_issues(root)
        checks += 1

        for primary_path in (DIRECT_CHECKER, ALIGNMENT_CHECKER, FIXTURE):
            build_sample_root(root)
            resolve_path(root, primary_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
            else:
                raise AssertionError(f"missing primary file did not abort: {primary_path}")
            checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_THREE_TARGET_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CROSS_THREE_TARGET_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 three-target direct cross packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_THREE_TARGET_PACKET=pass")
    print(f"PHASE2_CROSS_THREE_TARGET_PACKET_TARGET_COUNT={len(EXPECTED_FIXTURE['cross_targets'])}")
    print(
        "PHASE2_CROSS_THREE_TARGET_PACKET_ARCHIVE_SCOPE_COUNT="
        f"{len(EXPECTED_FIXTURE['archive_target_scope'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
