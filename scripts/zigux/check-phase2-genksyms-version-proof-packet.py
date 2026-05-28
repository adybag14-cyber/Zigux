#!/usr/bin/env python3
"""Guard the shipped Lane 24 genksyms version-proof packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase2.py")
CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

PROOF_RELS = (
    Path("scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"),
    Path("scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"),
)

VALIDATOR_MARKERS = tuple(f'"{proof.as_posix()}",' for proof in PROOF_RELS)
CLOSURE_MARKERS = tuple(f"`{proof.as_posix()}`" for proof in PROOF_RELS)
TOOL_MANIFEST_PACKET = "bridge_helpers"
GENKSYMS_PROOF_PACKET = "standalone_proof_packet"


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_string_list(
    issues: list[tuple[str, str]], payload: dict[str, object], key: str
) -> list[str] | None:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_PACKET", key))
        return None
    return list(value)


def require_present_surfaces_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_TOOL_MANIFEST", "present_surfaces"))
        return None
    return require_string_list(issues, surfaces, key)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    required_files = (
        VALIDATOR_REL,
        CLOSURE_REL,
        TOOL_MANIFEST_REL,
        GENKSYMS_MANIFEST_REL,
        *PROOF_RELS,
    )
    for rel in required_files:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    validator_text = read_text(resolve(root, VALIDATOR_REL))
    closure_text = read_text(resolve(root, CLOSURE_REL))
    tool_manifest = read_json(resolve(root, TOOL_MANIFEST_REL))
    genksyms_manifest = read_json(resolve(root, GENKSYMS_MANIFEST_REL))

    if not isinstance(tool_manifest, dict):
        issues.append(("INVALID_TOOL_MANIFEST", "root"))
        return issues
    if not isinstance(genksyms_manifest, dict):
        issues.append(("INVALID_GENKSYMS_MANIFEST", "root"))
        return issues

    for marker in VALIDATOR_MARKERS:
        count = count_exact_lines(validator_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MARKER", f"{marker}:count={count}"))

    for marker in CLOSURE_MARKERS:
        count = closure_text.count(marker)
        if count == 0:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CLOSURE_MARKER", f"{marker}:count={count}"))

    bridge_helpers = require_present_surfaces_list(issues, tool_manifest, TOOL_MANIFEST_PACKET)
    if bridge_helpers is not None:
        for proof in PROOF_RELS:
            proof_str = proof.as_posix()
            count = bridge_helpers.count(proof_str)
            if count == 0:
                issues.append(("MISSING_TOOL_MANIFEST_PROOF", proof_str))
            elif count != 1:
                issues.append(("DUPLICATE_TOOL_MANIFEST_PROOF", f"{proof_str}:count={count}"))

    standalone_proof_packet = require_string_list(
        issues, genksyms_manifest, GENKSYMS_PROOF_PACKET
    )
    if standalone_proof_packet is not None:
        for proof in PROOF_RELS:
            proof_str = proof.as_posix()
            count = standalone_proof_packet.count(proof_str)
            if count == 0:
                issues.append(("MISSING_GENKSYMS_PROOF", proof_str))
            elif count != 1:
                issues.append(("DUPLICATE_GENKSYMS_PROOF", f"{proof_str}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_GENKSYMS_VERSION_PROOF_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    validator_lines = [
        "GENKSYMS_PROOFS = (",
        *[f"    {marker}" for marker in VALIDATOR_MARKERS],
        ")",
        "",
    ]
    closure_lines = [
        "# Phase 2 Closure",
        "Current genksyms version-proof packet:",
        *[f"- {marker}" for marker in CLOSURE_MARKERS],
        "",
    ]
    tool_manifest = {
        "present_surfaces": {
            TOOL_MANIFEST_PACKET: [proof.as_posix() for proof in PROOF_RELS],
        }
    }
    genksyms_manifest = {
        GENKSYMS_PROOF_PACKET: [proof.as_posix() for proof in PROOF_RELS],
    }

    write_text(resolve(root, VALIDATOR_REL), "\n".join(validator_lines))
    write_text(resolve(root, CLOSURE_REL), "\n".join(closure_lines))
    write_text(resolve(root, TOOL_MANIFEST_REL), json.dumps(tool_manifest, indent=2) + "\n")
    write_text(
        resolve(root, GENKSYMS_MANIFEST_REL),
        json.dumps(genksyms_manifest, indent=2) + "\n",
    )
    for proof in PROOF_RELS:
        write_text(resolve(root, proof), "test \"placeholder\" {}\n")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="lane24_genksyms_version_proof_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            replace_exact_line(
                validator_path.read_text(encoding="utf-8"),
                VALIDATOR_MARKERS[0],
                '    "scripts/zigux/other_test.zig",',
            ),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_MARKER", VALIDATOR_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        closure_path = resolve(root, CLOSURE_REL)
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[1], "", 1),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_MARKER", CLOSURE_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        tool_manifest_path = resolve(root, TOOL_MANIFEST_REL)
        payload = json.loads(tool_manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"][TOOL_MANIFEST_PACKET].remove(PROOF_RELS[0].as_posix())
        tool_manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_TOOL_MANIFEST_PROOF", PROOF_RELS[0].as_posix()) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        genksyms_manifest_path = resolve(root, GENKSYMS_MANIFEST_REL)
        payload = json.loads(genksyms_manifest_path.read_text(encoding="utf-8"))
        payload[GENKSYMS_PROOF_PACKET].remove(PROOF_RELS[1].as_posix())
        genksyms_manifest_path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        assert ("MISSING_GENKSYMS_PROOF", PROOF_RELS[1].as_posix()) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        resolve(root, PROOF_RELS[0]).unlink()
        assert ("MISSING_REQUIRED_FILE", PROOF_RELS[0].as_posix()) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        tool_manifest_path = resolve(root, TOOL_MANIFEST_REL)
        payload = json.loads(tool_manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"][TOOL_MANIFEST_PACKET].append(PROOF_RELS[0].as_posix())
        tool_manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        duplicate_issue = (
            "DUPLICATE_TOOL_MANIFEST_PROOF",
            f"{PROOF_RELS[0].as_posix()}:count=2",
        )
        assert duplicate_issue in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        genksyms_manifest_path = resolve(root, GENKSYMS_MANIFEST_REL)
        payload = json.loads(genksyms_manifest_path.read_text(encoding="utf-8"))
        payload[GENKSYMS_PROOF_PACKET] = [123]
        genksyms_manifest_path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        assert ("INVALID_PACKET", GENKSYMS_PROOF_PACKET) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        tool_manifest_path = resolve(root, TOOL_MANIFEST_REL)
        payload = json.loads(tool_manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"] = []
        tool_manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_TOOL_MANIFEST", "present_surfaces") in collect_issues(root)
        checks_run += 1

    print("PHASE2_GENKSYMS_VERSION_PROOF_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_VERSION_PROOF_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the shipped Lane 24 genksyms version-proof packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for local packet validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(
            "PHASE2_GENKSYMS_VERSION_PROOF_PACKET_SAMPLE_ROOT="
            f"{args.write_sample_root.resolve()}"
        )
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_VERSION_PROOF_PACKET=pass")
    print(f"PHASE2_GENKSYMS_VERSION_PROOF_PACKET_PROOF_COUNT={len(PROOF_RELS)}")
    print("PHASE2_GENKSYMS_VERSION_PROOF_PACKET_REQUIRED_FILE_COUNT=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
