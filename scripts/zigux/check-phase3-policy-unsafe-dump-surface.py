#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
POLICY_TEST_REL = "zigux/tests/phase3_policy_unsafe.zig"
MAKEFILE_REL = "zigux/Makefile"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
PLACEHOLDER_SHA = "0123456789abcdef0123456789abcdef01234567"
PLACEHOLDER_COMMIT = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig",
    "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/tests/phase3_abi_dump.zig`",
    "`unsafe_scope_none`, `unsafe_scope_volatile_mmio`, `unsafe_scope_raw_pointer_bridge`, and `zigux_rbtree_root_view`",
    "canonical ABI dump path",
)

REQUIRED_ABI_DUMP_SNIPPETS = (
    '"unsafe_scope_none"',
    '"unsafe_scope_volatile_mmio"',
    '"unsafe_scope_raw_pointer_bridge"',
    '"zigux_interop_policy"',
    '"zigux_rbtree_root_view"',
)

REQUIRED_POLICY_TEST_SNIPPETS = (
    'test "phase3 policy layout stays explicit at the ABI boundary"',
    "layout_assert.assertInteropPolicyLayout();",
    'test "phase3 policy gate decodes interop-policy unsafe bytes explicitly"',
)

REQUIRED_MAKEFILE_SNIPPETS = (
    "$(ZIG) build phase3-dump --build-file zigux/tests/build.zig",
    "$(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
)

SURVEYED_PACKET_BLOB_MARKERS = {
    "PHASE3_ABI_DUMP_BLOB_SHA": ABI_DUMP_REL,
}


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _check_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def _marker_value_from_text(text: str, marker: str) -> str | None:
    prefix = f"{marker}="
    for line in text.splitlines():
        stripped = line.strip().strip("- ").strip("`")
        if stripped.startswith(prefix):
            return stripped[len(prefix) :]
    return None


def _replace_blob_markers_with_head(root: Path, survey_path: Path) -> None:
    survey_text = survey_path.read_text(encoding="utf-8")
    for marker, rel in SURVEYED_PACKET_BLOB_MARKERS.items():
        blob_sha = subprocess.run(
            ["git", "hash-object", "--no-filters", str(root / rel)],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        survey_text = survey_text.replace(f"{marker}={PLACEHOLDER_SHA}", f"{marker}={blob_sha}")
    survey_path.write_text(survey_text, encoding="utf-8", newline="\n")


def _packet_drift_by_blob_sha(root: Path, survey: str) -> list[str]:
    if not (root / ".git").exists():
        return []

    issues: list[str] = []
    for marker, rel in SURVEYED_PACKET_BLOB_MARKERS.items():
        expected_blob = _marker_value_from_text(survey, marker)
        if expected_blob is None:
            issues.append(f"missing_survey_marker:{marker}=")
            continue
        if not HEX40.fullmatch(expected_blob):
            issues.append(f"invalid_survey_blob_sha:{marker}:{expected_blob}")
            continue

        path = root / rel
        if not path.exists():
            issues.append(f"current_blob_unavailable:{rel}")
            continue

        current_blob = subprocess.run(
            ["git", "hash-object", "--no-filters", str(path)],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if current_blob != expected_blob:
            issues.append(f"surveyed_blob_drift:{rel}")

    return issues


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    abi_dump = _read_text(root, ABI_DUMP_REL, issues)
    policy_test = _read_text(root, POLICY_TEST_REL, issues)
    makefile = _read_text(root, MAKEFILE_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)
        issues.extend(_packet_drift_by_blob_sha(root, survey))
    if abi_dump:
        _check_snippets(abi_dump, REQUIRED_ABI_DUMP_SNIPPETS, "missing_abi_dump_snippet", issues)
    if policy_test:
        _check_snippets(policy_test, REQUIRED_POLICY_TEST_SNIPPETS, "missing_policy_test_snippet", issues)
    if makefile:
        _check_snippets(makefile, REQUIRED_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)

    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_dump_surface_") as tmp_dir_str:
        root = Path(tmp_dir_str)

        _write(
            root,
            SURVEY_REL,
            "\n".join(
                (
                    "# Phase 3 Policy and Unsafe Boundary Survey",
                    "",
                    f"- `PHASE3_SURVEYED_COMMIT={PLACEHOLDER_COMMIT}`",
                    "- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`",
                    f"- `PHASE3_ABI_DUMP_BLOB_SHA={PLACEHOLDER_SHA}`",
                    "- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`",
                    "",
                    "This note keeps `zigux/tests/phase3_abi_dump.zig` on the canonical ABI dump path.",
                    "It records `unsafe_scope_none`, `unsafe_scope_volatile_mmio`, `unsafe_scope_raw_pointer_bridge`, and `zigux_rbtree_root_view` on that canonical ABI dump path.",
                    "",
                )
            )
            + "\n",
        )
        _write(
            root,
            ABI_DUMP_REL,
            "\n".join(REQUIRED_ABI_DUMP_SNIPPETS) + "\n",
        )
        _write(
            root,
            POLICY_TEST_REL,
            "\n".join(REQUIRED_POLICY_TEST_SNIPPETS) + "\n",
        )
        _write(
            root,
            MAKEFILE_REL,
            "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n",
        )

        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Codex",
            "GIT_AUTHOR_EMAIL": "codex@example.com",
            "GIT_COMMITTER_NAME": "Codex",
            "GIT_COMMITTER_EMAIL": "codex@example.com",
        }
        subprocess.run(
            ["git", "commit", "-m", "self-test snapshot"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        survey_path = root / SURVEY_REL
        survey_path.writeText if False else None
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(PLACEHOLDER_COMMIT, head),
            encoding="utf-8",
            newline="\n",
        )
        _replace_blob_markers_with_head(root, survey_path)

        assert validate(root) == []

        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
                "PHASE3_DUMP_GATE=missing",
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert "missing_survey_marker:PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig" in issues

        _write(
            root,
            SURVEY_REL,
            "\n".join(
                (
                    "# Phase 3 Policy and Unsafe Boundary Survey",
                    "",
                    f"- `PHASE3_SURVEYED_COMMIT={head}`",
                    "- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`",
                    f"- `PHASE3_ABI_DUMP_BLOB_SHA={PLACEHOLDER_SHA}`",
                    "- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`",
                    "",
                    "This note keeps `zigux/tests/phase3_abi_dump.zig` on the canonical ABI dump path.",
                    "It records `unsafe_scope_none`, `unsafe_scope_volatile_mmio`, `unsafe_scope_raw_pointer_bridge`, and `zigux_rbtree_root_view` on that canonical ABI dump path.",
                    "",
                )
            )
            + "\n",
        )
        _replace_blob_markers_with_head(root, survey_path)
        _write(root, ABI_DUMP_REL, (root / ABI_DUMP_REL).read_text(encoding="utf-8") + "// drift\n")
        issues = validate(root)
        assert f"surveyed_blob_drift:{ABI_DUMP_REL}" in issues

        _write(root, ABI_DUMP_REL, "\n".join(REQUIRED_ABI_DUMP_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert 'missing_abi_dump_snippet:"zigux_rbtree_root_view"' in issues

    print("PHASE3_POLICY_UNSAFE_DUMP_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the Phase 3 policy and unsafe packet keeps its shared ABI dump evidence explicit."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_POLICY_UNSAFE_DUMP_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_POLICY_UNSAFE_DUMP_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
