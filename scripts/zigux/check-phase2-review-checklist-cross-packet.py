#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
PHASE2_CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

REVIEW_CHECKLIST_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-cross`",
    "installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = (
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`make -C zigux phase2-cross`",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-cross`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, kconfig bridge checker, genksyms bridge, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_cross_target_issues(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_CROSS_TARGETS_JSON", "top-level value must be an object")]

    issues: list[tuple[str, str]] = []
    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_CROSS_TARGETS_FIELD", f"phase::{payload.get('phase')!r}"))
    if payload.get("status") != "active":
        issues.append(("INVALID_CROSS_TARGETS_FIELD", f"status::{payload.get('status')!r}"))
    if payload.get("route") != "make -C zigux phase2-cross":
        issues.append(("INVALID_CROSS_TARGETS_FIELD", f"route::{payload.get('route')!r}"))

    archive_target_scope = payload.get("archive_target_scope")
    if archive_target_scope != ["x86_64-linux"]:
        issues.append(("INVALID_CROSS_TARGETS_FIELD", f"archive_target_scope::{archive_target_scope!r}"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list):
        return issues + [("INVALID_CROSS_TARGETS_FIELD", f"cross_targets::{cross_targets!r}")]

    expected_targets = {
        "x86_64-linux": {
            "review_status": "pinned bootstrap archive",
            "validation_mode": "archive_required",
            "route": "make -C zigux phase2-cross",
        },
        "aarch64-linux": {
            "review_status": "route contract only",
            "validation_mode": "route_contract_only",
            "route": "make -C zigux phase2-cross",
        },
    }

    actual_targets: dict[str, object] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGETS_ENTRY", repr(entry)))
            continue
        target = entry.get("target")
        if not isinstance(target, str):
            issues.append(("INVALID_CROSS_TARGETS_ENTRY", repr(entry)))
            continue
        actual_targets[target] = entry

    for target, expected_entry in expected_targets.items():
        actual_entry = actual_targets.get(target)
        if actual_entry is None:
            issues.append(("MISSING_CROSS_TARGET", target))
            continue
        for key, expected_value in expected_entry.items():
            actual_value = actual_entry.get(key) if isinstance(actual_entry, dict) else None
            if actual_value != expected_value:
                issues.append(
                    (
                        "INVALID_CROSS_TARGET_ENTRY",
                        f"{target}::{key}::{actual_value!r}",
                    )
                )

    if len(actual_targets) != len(expected_targets):
        issues.append(("INVALID_CROSS_TARGET_COUNT", str(len(actual_targets))))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    phase2_cross_targets = read_json(resolve_path(root, PHASE2_CROSS_TARGETS))

    issues = collect_missing_markers(
        review_checklist_text,
        REVIEW_CHECKLIST_MARKERS,
        "MISSING_REVIEW_CHECKLIST_MARKER",
    )
    issues.extend(
        collect_exact_count_markers(
            review_checklist_text,
            REVIEW_CHECKLIST_EXACT_COUNT_MARKERS,
            "REVIEW_CHECKLIST_EXACT_COUNT_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text,
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKER",
        )
    )
    issues.extend(collect_cross_target_issues(phase2_cross_targets))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_REVIEW_CHECKLIST_CROSS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(
        resolve_path(root, PHASE2_CROSS_TARGETS),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": "make -C zigux phase2-cross",
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": "make -C zigux phase2-cross",
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": "make -C zigux phase2-cross",
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def remove_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(REVIEW_CHECKLIST_EXACT_COUNT_MARKERS)
        + len(TESTS_README_MARKERS)
        + 4
        + 3
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_cross_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(remove_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_CHECKLIST_MARKER", marker) in issues
            checks_run += 1

        for marker in REVIEW_CHECKLIST_EXACT_COUNT_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("REVIEW_CHECKLIST_EXACT_COUNT_MARKER", f"2::{marker}") in issues
            checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(remove_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKER", marker) in issues
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, PHASE2_CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["route"] = "make -C zigux phase2-tools"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_CROSS_TARGETS_FIELD", "route::'make -C zigux phase2-tools'") in issues
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, PHASE2_CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["review_status"] = "route contract only"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "INVALID_CROSS_TARGET_ENTRY",
            "x86_64-linux::review_status::'route contract only'",
        ) in issues
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, PHASE2_CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"] = payload["cross_targets"][:1]
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_CROSS_TARGET", "aarch64-linux") in issues
        assert ("INVALID_CROSS_TARGET_COUNT", "1") in issues
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, PHASE2_CROSS_TARGETS)
        path.write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_CROSS_TARGETS_JSON", "top-level value must be an object") in issues
        checks_run += 1

        for rel_path in (REVIEW_CHECKLIST, TESTS_README, PHASE2_CROSS_TARGETS):
            build_sample_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_REVIEW_CHECKLIST_CROSS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_CROSS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the review-checklist Phase 2 direct cross-route packet drifts below tests-root and fixture evidence."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("PHASE2_REVIEW_CHECKLIST_CROSS_PACKET_SAMPLE_ROOT=written")
        print(f"PHASE2_REVIEW_CHECKLIST_CROSS_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_CROSS_PACKET=pass")
    print(
        "PHASE2_REVIEW_CHECKLIST_CROSS_PACKET_REVIEW_MARKER_COUNT="
        f"{len(REVIEW_CHECKLIST_MARKERS)}"
    )
    print(
        "PHASE2_REVIEW_CHECKLIST_CROSS_PACKET_TESTS_MARKER_COUNT="
        f"{len(TESTS_README_MARKERS)}"
    )
    print("PHASE2_REVIEW_CHECKLIST_CROSS_PACKET_TARGET_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
