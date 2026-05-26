#!/usr/bin/env python3
"""Guard the shared Phase 2 closure status and restore-state packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
BOOTSTRAP_NOTE = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
DOCS_README = Path("Documentation/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")
MAKEFILE = Path("zigux/Makefile")

EXPECTED_STATUS = "parked"
EXPECTED_RESTORE_STATE = "docs_plus_manifest"
EXPECTED_AUTHORITY_SNIPPETS = (
    "current authority: this closure note, the committed Phase 2 tool manifest, the toolchain bootstrap note",
    "the returned closure-side validator pair",
    "the shipped `zigux/Makefile` wrappers",
    "the current kconfig, genksyms, fixdep, artifact-support, plus cross-route fixture manifests remain the trustworthy current-master sources",
)
REQUIRED_CLOSURE_REFERENCES = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
)
REQUIRED_README_HINTS = (
    (DOCS_README, "Phase 2 notes"),
    (TESTS_README, "## Phase 2 review packet"),
    (SCRIPTS_README, "## Phase 2"),
)
REQUIRED_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)
REQUIRED_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(root: Path, rel: Path) -> str:
    path = resolve(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = resolve(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(root: Path, rel: Path) -> object:
    path = resolve(root, rel)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc


def extract_assignment_value(text: str, key: str) -> str | None:
    needle = f"`{key}="
    for line in text.splitlines():
        if needle not in line:
            continue
        start = line.index(needle) + 1
        payload = line[start:].split("`", 1)[0]
        return payload.split("=", 1)[1]
    return None


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(root, PHASE2_CLOSURE)
    bootstrap_text = read_text(root, BOOTSTRAP_NOTE)
    docs_text = read_text(root, DOCS_README)
    tests_text = read_text(root, TESTS_README)
    scripts_text = read_text(root, SCRIPTS_README)
    read_text(root, VALIDATE_PHASE2)
    read_text(root, VALIDATE_PHASE2_CLOSURE)
    read_text(root, MAKEFILE)

    manifest = read_json(root, PHASE2_TOOL_MANIFEST)
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_TOP_LEVEL", str(PHASE2_TOOL_MANIFEST)))
        return issues

    status_value = extract_assignment_value(closure_text, "PHASE2_STATUS")
    if status_value is None:
        issues.append(("MISSING_ASSIGNMENT", "PHASE2_STATUS"))
    elif status_value != EXPECTED_STATUS:
        issues.append(("STATUS_MISMATCH", status_value))

    restore_state_value = extract_assignment_value(closure_text, "PHASE2_CLOSURE_RESTORE_STATE")
    if restore_state_value is None:
        issues.append(("MISSING_ASSIGNMENT", "PHASE2_CLOSURE_RESTORE_STATE"))
    elif restore_state_value != EXPECTED_RESTORE_STATE:
        issues.append(("RESTORE_STATE_MISMATCH", restore_state_value))

    if count_exact_lines(closure_text, f"- `PHASE2_STATUS={EXPECTED_STATUS}`") != 1:
        issues.append(("DUPLICATE_OR_MISSING_STATUS_LINE", EXPECTED_STATUS))
    if count_exact_lines(
        closure_text,
        f"- `PHASE2_CLOSURE_RESTORE_STATE={EXPECTED_RESTORE_STATE}`",
    ) != 1:
        issues.append(("DUPLICATE_OR_MISSING_RESTORE_STATE_LINE", EXPECTED_RESTORE_STATE))

    for snippet in EXPECTED_AUTHORITY_SNIPPETS:
        if snippet not in closure_text:
            issues.append(("MISSING_AUTHORITY_SNIPPET", snippet))

    for ref in REQUIRED_CLOSURE_REFERENCES:
        if ref not in closure_text and ref not in bootstrap_text:
            issues.append(("MISSING_SHARED_REFERENCE", ref))

    for rel, marker in REQUIRED_README_HINTS:
        text = {
            DOCS_README: docs_text,
            TESTS_README: tests_text,
            SCRIPTS_README: scripts_text,
        }[rel]
        if marker not in text:
            issues.append(("MISSING_README_HINT", f"{rel}:{marker}"))

    if manifest.get("status") != "active":
        issues.append(("MANIFEST_STATUS_MISMATCH", json.dumps(manifest.get("status"))))

    scope = manifest.get("scope")
    if not isinstance(scope, str) or "tranche-closure reminder packet" not in scope:
        issues.append(("MANIFEST_SCOPE_MISMATCH", json.dumps(scope)))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("MISSING_PRESENT_SURFACES", str(PHASE2_TOOL_MANIFEST)))
        return issues

    review_surfaces = present_surfaces.get("review_surfaces")
    if not isinstance(review_surfaces, list):
        issues.append(("MISSING_REVIEW_SURFACES", str(PHASE2_TOOL_MANIFEST)))
    else:
        for surface in REQUIRED_REVIEW_SURFACES:
            if surface not in review_surfaces:
                issues.append(("MISSING_REVIEW_SURFACE", surface))

    validators = present_surfaces.get("validators")
    if not isinstance(validators, list):
        issues.append(("MISSING_VALIDATORS", str(PHASE2_TOOL_MANIFEST)))
    else:
        for validator in REQUIRED_VALIDATORS:
            if validator not in validators:
                issues.append(("MISSING_VALIDATOR", validator))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_STATE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                "## Status",
                "",
                "- `PHASE2_STATUS=parked`",
                "- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`",
                "- current authority: this closure note, the committed Phase 2 tool manifest, the toolchain bootstrap note, the live toolchain, local-first archive, archive-verification, staged-archive helper, installer, cross-route, reminder, pinning, manifest, artifact helper, fixdep guards, the helper-local kconfig allconfig guard, the returned closure-side validator pair, the shipped `zigux/Makefile` wrappers, and the current kconfig, genksyms, fixdep, artifact-support, plus cross-route fixture manifests remain the trustworthy current-master sources for the bounded Phase 2 tranche",
                "",
                "## Current Closure Packet",
                "",
                "- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
                "- `scripts/zigux/validate-phase2.py`",
                "- `scripts/zigux/validate-phase2-closure.py`",
                "- `zigux/Makefile`",
                "- `zigux/tests/fixtures/phase2_tool_manifest.json`",
                "",
            )
        )
        + "\n",
    )
    write_text(
        root,
        BOOTSTRAP_NOTE,
        "# Phase 2 Toolchain Bootstrap Notes\n\n`zigux/Makefile`\n",
    )
    write_text(root, DOCS_README, "# Zigux\n\n## Phase 2 notes\n")
    write_text(root, TESTS_README, "# zigux/tests\n\n## Phase 2 review packet\n")
    write_text(root, SCRIPTS_README, "# scripts/zigux\n\n## Phase 2\n")
    write_text(root, VALIDATE_PHASE2, "print('phase2')\n")
    write_text(root, VALIDATE_PHASE2_CLOSURE, "print('phase2-closure')\n")
    write_text(root, MAKEFILE, "phase2:\n\t@true\n")
    write_text(
        root,
        PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
                "present_surfaces": {
                    "review_surfaces": list(REQUIRED_REVIEW_SURFACES),
                    "validators": list(REQUIRED_VALIDATORS),
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_state_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        write_text(root, PHASE2_CLOSURE, "# missing\n")
        issues = collect_issues(root)
        assert ("MISSING_ASSIGNMENT", "PHASE2_STATUS") in issues
        checks += 1

        build_sample_root(root)
        closure_text = read_text(root, PHASE2_CLOSURE).replace(
            "- `PHASE2_STATUS=parked`",
            "- `PHASE2_STATUS=active`",
        )
        write_text(root, PHASE2_CLOSURE, closure_text)
        issues = collect_issues(root)
        assert ("STATUS_MISMATCH", "active") in issues
        checks += 1

        build_sample_root(root)
        closure_text = read_text(root, PHASE2_CLOSURE).replace(
            "- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`",
            "- `PHASE2_CLOSURE_RESTORE_STATE=manifest_only`",
        )
        write_text(root, PHASE2_CLOSURE, closure_text)
        issues = collect_issues(root)
        assert ("RESTORE_STATE_MISMATCH", "manifest_only") in issues
        checks += 1

        build_sample_root(root)
        write_text(root, DOCS_README, "# Zigux\n")
        issues = collect_issues(root)
        assert ("MISSING_README_HINT", "Documentation/zigux/README.md:Phase 2 notes") in issues
        checks += 1

        build_sample_root(root)
        manifest = read_json(root, PHASE2_TOOL_MANIFEST)
        assert isinstance(manifest, dict)
        manifest["status"] = "parked"
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MANIFEST_STATUS_MISMATCH", '"parked"') in issues
        checks += 1

        build_sample_root(root)
        manifest = read_json(root, PHASE2_TOOL_MANIFEST)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["review_surfaces"] = [
            surface
            for surface in manifest["present_surfaces"]["review_surfaces"]
            if surface != "Documentation/zigux/phase2-closure.md"
        ]
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_REVIEW_SURFACE", "Documentation/zigux/phase2-closure.md") in issues
        checks += 1

        build_sample_root(root)
        manifest = read_json(root, PHASE2_TOOL_MANIFEST)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["validators"] = ["scripts/zigux/validate-phase2.py"]
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR", "scripts/zigux/validate-phase2-closure.py") in issues
        checks += 1

    print("PHASE2_CLOSURE_STATE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_STATE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 2 closure status and restore-state packet."
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in regression coverage")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a synthetic passing sample root and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_STATE_PACKET=pass")
    print("PHASE2_CLOSURE_STATE_PACKET_STATUS=parked")
    print("PHASE2_CLOSURE_STATE_PACKET_RESTORE_STATE=docs_plus_manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
