#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 cross-route contract packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_MAKE_ROUTES = [
    "phase2-toolchain",
    "phase2-validate",
    "phase2-cross",
]
EXPECTED_CROSS_TARGETS = [
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
]
BOOTSTRAP_NOTE_MARKERS = (
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "shared cross selftest-alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross selftest-alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "Linux-style cross route: `make -C zigux phase2-cross`",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
)
MAKEFILE_HEADER = "phase2-cross:"
MAKEFILE_MARKERS = (
    "check-phase2-cross.py --self-test",
    "check-phase2-cross.py",
    "check-phase2-cross-selftest-alignment.py --self-test",
    "check-phase2-cross-selftest-alignment.py",
)
EXPECTED_SELF_TEST_CASE_COUNT = 17


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


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected_object")]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY", "archive_sha256"))
    elif list(archive_sha256.keys()) != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_POLICY", f"archive_sha256_keys={list(archive_sha256.keys())!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY", "upgrade_policy"))
        return issues

    if upgrade_policy.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_POLICY", "archive_target_scope"))
    if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_MAKE_ROUTES:
        issues.append(("INVALID_POLICY", "required_make_routes"))
    return issues


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, FIXTURE))
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE", "expected_object")]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_FIXTURE", f"phase={payload.get('phase')!r}"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_FIXTURE", f"status={payload.get('status')!r}"))
    if payload.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE", f"route={payload.get('route')!r}"))
    if payload.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_FIXTURE", "archive_target_scope"))
    if payload.get("cross_targets") != EXPECTED_CROSS_TARGETS:
        issues.append(("INVALID_FIXTURE", "cross_targets"))
    return issues


def collect_bootstrap_note_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    for marker in BOOTSTRAP_NOTE_MARKERS:
        count = text.count(marker)
        if count == 0:
            issues.append(("MISSING_BOOTSTRAP_NOTE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_BOOTSTRAP_NOTE_MARKER", f"{marker}:count={count}"))
    return issues


def collect_makefile_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    text = read_text(resolve_path(root, MAKEFILE))
    header_count = sum(1 for line in text.splitlines() if line.startswith(MAKEFILE_HEADER))
    if header_count == 0:
        issues.append(("MISSING_MAKEFILE_HEADER", MAKEFILE_HEADER))
    elif header_count != 1:
        issues.append(("DUPLICATE_MAKEFILE_HEADER", f"{MAKEFILE_HEADER}:count={header_count}"))

    for marker in MAKEFILE_MARKERS:
        count = text.count(marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_MARKER", marker))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_policy_issues(root))
    issues.extend(collect_fixture_issues(root))
    issues.extend(collect_bootstrap_note_issues(root))
    issues.extend(collect_makefile_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_ROUTE_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_MAKE_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
                "route": ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": EXPECTED_CROSS_TARGETS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, BOOTSTRAP_NOTES),
        "# notes\n" + "\n".join(f"- {marker}" for marker in BOOTSTRAP_NOTE_MARKERS) + "\n",
    )
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(
            (
                "phase2-cross: phase2-toolchain",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_route_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "required_make_routes") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_sha256"]["aarch64-linux"] = "4" * 64
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "archive_sha256_keys=['x86_64-linux', 'aarch64-linux']") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["route"] = "make -C zigux phase2"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE", "route='make -C zigux phase2'") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"] = list(reversed(payload["cross_targets"]))
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE", "cross_targets") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["review_status"] = "pinned bootstrap archive"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE", "cross_targets") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, BOOTSTRAP_NOTES)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), BOOTSTRAP_NOTE_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_BOOTSTRAP_NOTE_MARKER", BOOTSTRAP_NOTE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, BOOTSTRAP_NOTES)
        text = path.read_text(encoding="utf-8")
        path.write_text(text + f"- {BOOTSTRAP_NOTE_MARKERS[0]}\n", encoding="utf-8")
        assert (
            "DUPLICATE_BOOTSTRAP_NOTE_MARKER",
            f"{BOOTSTRAP_NOTE_MARKERS[0]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), "phase2-cross: phase2-toolchain"), encoding="utf-8")
        assert ("MISSING_MAKEFILE_HEADER", MAKEFILE_HEADER) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        text = path.read_text(encoding="utf-8")
        path.write_text(text + "phase2-cross: phase2-toolchain\n", encoding="utf-8")
        assert ("DUPLICATE_MAKEFILE_HEADER", f"{MAKEFILE_HEADER}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_MAKEFILE_MARKER", MAKEFILE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("[]\n", encoding="utf-8")
        assert ("INVALID_POLICY", "expected_object") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        path.write_text("[]\n", encoding="utf-8")
        assert ("INVALID_FIXTURE", "expected_object") in collect_issues(root)
        checks_run += 1

        for missing_path in (TOOLCHAIN_POLICY, FIXTURE, BOOTSTRAP_NOTES, MAKEFILE):
            build_self_test_root(root)
            resolve_path(root, missing_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing primary file did not abort: {missing_path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_ROUTE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current directly readable Phase 2 cross-route contract stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_ROUTE_CONTRACT=pass")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_TARGET_COUNT={len(EXPECTED_CROSS_TARGETS)}")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_ARCHIVE_SCOPE_COUNT={len(EXPECTED_ARCHIVE_SCOPE)}")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_REQUIRED_ROUTE_COUNT={len(EXPECTED_REQUIRED_MAKE_ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
