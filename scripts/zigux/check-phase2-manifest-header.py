#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_HEADER_FIELDS = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
}

REQUIRED_ROOT_KEYS = (
    "phase",
    "status",
    "scope",
    "present_surfaces",
    "notes",
    "repo_reality_gaps",
    "workflow",
)


class DuplicateKeyError(ValueError):
    pass


def strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateKeyError(key)
        payload[key] = value
    return payload


def read_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    try:
        payload = json.loads(raw, object_pairs_hook=strict_object_pairs)
    except DuplicateKeyError as exc:
        raise SystemExit(f"duplicate json key in required file: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_manifest() -> dict[str, Any]:
    return {
        "phase": REQUIRED_HEADER_FIELDS["phase"],
        "status": REQUIRED_HEADER_FIELDS["status"],
        "scope": REQUIRED_HEADER_FIELDS["scope"],
        "present_surfaces": {},
        "notes": [],
        "repo_reality_gaps": [],
        "workflow": ".github/workflows/zigux-bootstrap.yml",
    }


def build_sample_root(root: Path) -> None:
    if root.exists():
        for child in root.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    write_text(root / MANIFEST, json.dumps(build_sample_manifest(), indent=2) + "\n")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest = read_manifest(root / MANIFEST)
    issues: list[tuple[str, str]] = []

    for key in REQUIRED_ROOT_KEYS:
        if key not in manifest:
            issues.append(("MISSING_ROOT_KEY", key))

    for key, expected in REQUIRED_HEADER_FIELDS.items():
        if manifest.get(key) != expected:
            issues.append(("HEADER_FIELD_MISMATCH", key))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_ROOT_SHAPE", "present_surfaces"))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("INVALID_ROOT_SHAPE", "notes"))

    repo_reality_gaps = manifest.get("repo_reality_gaps")
    if repo_reality_gaps != []:
        issues.append(("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_MANIFEST_HEADER=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def run_self_test() -> int:
    expected_case_count = 11
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_manifest_header_") as tmp_dir:
        root = Path(tmp_dir)
        manifest_path = root / MANIFEST

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for key, replacement in (
            ("phase", "Phase X"),
            ("status", "parked"),
            ("scope", "drifted scope"),
        ):
            build_sample_root(root)
            manifest = build_sample_manifest()
            manifest[key] = replacement
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
            assert ("HEADER_FIELD_MISMATCH", key) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        manifest = build_sample_manifest()
        manifest["repo_reality_gaps"] = ["stale-gap"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps") in collect_issues(root)
        checks_run += 1

        for key, replacement in (
            ("present_surfaces", []),
            ("notes", {}),
        ):
            build_sample_root(root)
            manifest = build_sample_manifest()
            manifest[key] = replacement
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
            assert ("INVALID_ROOT_SHAPE", key) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        manifest = build_sample_manifest()
        del manifest["scope"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_ROOT_KEY", "scope") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        write_text(
            manifest_path,
            """{
  \"phase\": \"Phase 2\",
  \"phase\": \"shadowed\",
  \"status\": \"active\",
  \"scope\": \"current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet\",
  \"present_surfaces\": {},
  \"notes\": [],
  \"repo_reality_gaps\": [],
  \"workflow\": \".github/workflows/zigux-bootstrap.yml\"
}
""",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate json key" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate top-level key did not abort")

        build_sample_root(root)
        write_text(
            manifest_path,
            """{
  \"phase\": \"Phase 2\",
  \"status\": \"active\",
  \"scope\": \"current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet\",
  \"present_surfaces\": {
    \"review_surfaces\": [],
    \"review_surfaces\": []
  },
  \"notes\": [],
  \"repo_reality_gaps\": [],
  \"workflow\": \".github/workflows/zigux-bootstrap.yml\"
}
""",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate json key" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate nested key did not abort")

        build_sample_root(root)
        manifest_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_MANIFEST_HEADER_SELF_TEST=pass")
    print(f"PHASE2_MANIFEST_HEADER_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the top-level Phase 2 manifest header packet aligned with the current closure-state contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="exercise the checker against synthetic fixtures")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="write a passing current-like sample root to the chosen directory",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_MANIFEST_HEADER_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_MANIFEST_HEADER=pass")
    print(f"PHASE2_MANIFEST_HEADER_REQUIRED_FIELD_COUNT={len(REQUIRED_HEADER_FIELDS) + 1}")
    print(f"PHASE2_MANIFEST_HEADER_ROOT_KEY_COUNT={len(REQUIRED_ROOT_KEYS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
