#!/usr/bin/env python3
"""Guard the shared Phase 2 review-checklist toolchain pin-scope packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
TESTS_README = Path("zigux/tests/README.md")
TOOLCHAIN_PIN_SCOPE = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
TOOLCHAIN_CHECKER = Path("scripts/zigux/check-zig-toolchain.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

REVIEW_CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "same pinned toolchain",
)

BOOTSTRAP_NOTES_MARKERS = (
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`third_party/README.md`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "pinned-channel",
)

TESTS_README_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`third_party/README.md`",
    "pinned `x86_64-linux` bootstrap archive note",
    "repo-local `.zig-toolchain` fallback reused",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

TOOLCHAIN_PIN_SCOPE_MARKERS = (
    "REVIEW_CHECKLIST = ROOT / \"Documentation\" / \"zigux/review-checklist.md\"",
    "TESTS_README = ROOT / \"zigux/tests/README.md\"",
    "BOOTSTRAP_NOTES = ROOT / \"Documentation/zigux/phase2-toolchain-bootstrap-notes.md\"",
    "\"`make -C zigux phase2-tools`\"",
    "\"`make -C zigux phase2-kconfig`\"",
    "\"`make -C zigux phase2-cross`\"",
    "\"`make -C zigux phase2-validate`\"",
    "EXPECTED_REQUIRED_ROUTES = [",
    "\"phase2-tools\",",
    "\"phase2-kconfig\",",
    "\"phase2-cross\",",
    "\"phase2-validate\",",
    "def validate_policy(",
)

TOOLCHAIN_CHECKER_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    "def load_min_version(",
    "def load_pinned_channel(",
    "def iter_repo_local_zig_candidates(",
    "def resolve_zig_executable(",
    "def iter_repo_local_archive_candidates(",
    "def resolve_policy_archive(",
    "def expected_archive_metadata(",
    "def validate_policy_archive(",
    'parser.add_argument("--allow-missing"',
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2",
)

MAKEFILE_LINE_MARKERS = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)

MAKEFILE_EXACT_LINE_MARKERS = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)

EXPECTED_PHASE = "Phase 2"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGETS = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

FILE_MARKERS = (
    (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "REVIEW_CHECKLIST"),
    (BOOTSTRAP_NOTES, BOOTSTRAP_NOTES_MARKERS, "BOOTSTRAP_NOTES"),
    (TESTS_README, TESTS_README_MARKERS, "TESTS_README"),
    (TOOLCHAIN_PIN_SCOPE, TOOLCHAIN_PIN_SCOPE_MARKERS, "TOOLCHAIN_PIN_SCOPE"),
    (TOOLCHAIN_CHECKER, TOOLCHAIN_CHECKER_MARKERS, "TOOLCHAIN_CHECKER"),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, relpath: Path) -> Path:
    return root / relpath


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_marker_issues(text: str, markers: tuple[str, ...], code_prefix: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            issues.append((f"{code_prefix}_MARKER_MISSING", marker))
        elif count != 1:
            issues.append((f"{code_prefix}_MARKER_DUPLICATED", f"{marker}:count={count}"))
    return issues


def collect_exact_line_issues(text: str, markers: tuple[str, ...], code_prefix: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((f"{code_prefix}_MARKER_MISSING", marker))
        elif count != 1:
            issues.append((f"{code_prefix}_MARKER_DUPLICATED", f"{marker}:count={count}"))
    return issues


def validate_policy(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("TOOLCHAIN_POLICY_INVALID", "expected JSON object")]

    issues: list[tuple[str, str]] = []
    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("TOOLCHAIN_POLICY_INVALID", f"phase={payload.get('phase')!r}"))
    if payload.get("channel") != EXPECTED_CHANNEL:
        issues.append(("TOOLCHAIN_POLICY_INVALID", f"channel={payload.get('channel')!r}"))
    if payload.get("minimum_version") != EXPECTED_CHANNEL:
        issues.append(("TOOLCHAIN_POLICY_INVALID", f"minimum_version={payload.get('minimum_version')!r}"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("TOOLCHAIN_POLICY_INVALID", "archive_sha256"))
    else:
        if list(archive_sha256.keys()) != EXPECTED_TARGETS:
            issues.append(("TOOLCHAIN_POLICY_INVALID", f"archive_sha256_keys={list(archive_sha256.keys())!r}"))
        digest = archive_sha256.get("x86_64-linux")
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            issues.append(("TOOLCHAIN_POLICY_INVALID", "archive_sha256[x86_64-linux]"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("TOOLCHAIN_POLICY_INVALID", "upgrade_policy"))
    else:
        if upgrade_policy.get("channel_minimum_lockstep") is not True:
            issues.append(("TOOLCHAIN_POLICY_INVALID", "channel_minimum_lockstep"))
        if upgrade_policy.get("archive_target_scope") != EXPECTED_TARGETS:
            issues.append(("TOOLCHAIN_POLICY_INVALID", "archive_target_scope"))
        if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_ROUTES:
            issues.append(("TOOLCHAIN_POLICY_INVALID", "required_make_routes"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for relpath, markers, code_prefix in FILE_MARKERS:
        issues.extend(
            collect_marker_issues(
                read_text(resolve_path(root, relpath)),
                markers,
                code_prefix,
            )
        )

    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, WORKFLOW)),
            WORKFLOW_MARKERS,
            "WORKFLOW",
        )
    )
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    issues.extend(collect_exact_line_issues(makefile_text, MAKEFILE_LINE_MARKERS, "MAKEFILE_LINE"))
    issues.extend(collect_exact_line_issues(makefile_text, MAKEFILE_EXACT_LINE_MARKERS, "MAKEFILE_EXACT_LINE"))

    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        issues.append(("TOOLCHAIN_POLICY_INVALID_JSON", exc.msg))
    else:
        issues.extend(validate_policy(payload))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET=fail")
    for code, detail in issues:
        print(f"{code}={detail}")
    return 1


def build_sample_root(root: Path) -> None:
    for relpath, markers, _ in FILE_MARKERS:
        write_text(resolve_path(root, relpath), "\n".join(markers) + "\n")

    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join([*MAKEFILE_LINE_MARKERS, *MAKEFILE_EXACT_LINE_MARKERS]) + "\n",
    )
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_TARGETS,
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def remove_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_pin_scope_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        review_path = resolve_path(root, REVIEW_CHECKLIST)
        missing_marker = REVIEW_CHECKLIST_MARKERS[0]
        review_path.write_text(replace_once(review_path.read_text(encoding="utf-8"), missing_marker), encoding="utf-8")
        assert (f"REVIEW_CHECKLIST_MARKER_MISSING", missing_marker) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        missing_workflow_line = WORKFLOW_MARKERS[0]
        workflow_path.write_text(remove_exact_line(workflow_path.read_text(encoding="utf-8"), missing_workflow_line), encoding="utf-8")
        assert (f"WORKFLOW_MARKER_MISSING", missing_workflow_line) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        duplicated_line = MAKEFILE_LINE_MARKERS[0]
        makefile_path.write_text(duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), duplicated_line), encoding="utf-8")
        assert (f"MAKEFILE_LINE_MARKER_DUPLICATED", f"{duplicated_line}:count=2") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        checker_path = resolve_path(root, TOOLCHAIN_CHECKER)
        missing_checker_marker = TOOLCHAIN_CHECKER_MARKERS[0]
        checker_path.write_text(replace_once(checker_path.read_text(encoding="utf-8"), missing_checker_marker), encoding="utf-8")
        assert (f"TOOLCHAIN_CHECKER_MARKER_MISSING", missing_checker_marker) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("TOOLCHAIN_POLICY_INVALID", "required_make_routes") in collect_issues(root)
        checks_run += 1

        for relpath in (REVIEW_CHECKLIST, BOOTSTRAP_NOTES, TESTS_README, TOOLCHAIN_PIN_SCOPE, TOOLCHAIN_CHECKER, WORKFLOW, MAKEFILE, TOOLCHAIN_POLICY):
            build_sample_root(root)
            resolve_path(root, relpath).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {relpath}")

    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", type=Path, help="write a focused passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        sample_root = args.write_sample_root.resolve()
        build_sample_root(sample_root)
        print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SAMPLE_ROOT={sample_root}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_REQUIRED_PATH_COUNT=8")
    print(
        "PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for _, markers, _ in FILE_MARKERS) + len(WORKFLOW_MARKERS) + len(MAKEFILE_LINE_MARKERS) + len(MAKEFILE_EXACT_LINE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
