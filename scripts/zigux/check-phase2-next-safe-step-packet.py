#!/usr/bin/env python3
"""Guard the shared Phase 2 closure next-step handoff packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parent
PHASE2_CLOSURE = "Documentation/zigux/phase2-closure.md"
DOCS_README = "Documentation/zigux/README.md"
TESTS_README = "zigux/tests/README.md"
SCRIPTS_README = "scripts/zigux/README.md"

EXPECTED_NEXT_SAFE_STEP = (
    "keep the shared Phase 2 closure packet parked unless one shared reminder "
    "surface drifts again; if the shared backlog reopens first, start with one "
    "smallest truthfulness repair in Documentation/zigux/README.md, zigux/tests/README.md, "
    "or the directly coupled shared checker that proves the drift, and keep "
    "fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes"
)

REQUIRED_NOTE_SNIPPETS = (
    "keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again",
    "start with one smallest truthfulness repair in `Documentation/zigux/README.md`, `zigux/tests/README.md`, or the directly coupled shared checker that proves the drift",
    "keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes",
)

REQUIRED_PATH_REFERENCES = (
    "Documentation/zigux/README.md",
    "zigux/tests/README.md",
)

FORBIDDEN_LANE_ESCALATIONS = (
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
)

REQUIRED_SHARED_PACKET_HINTS = ("Phase 2 notes",)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_assignment_value(text: str, key: str) -> str | None:
    needle = f"`{key}="
    for line in text.splitlines():
        if needle not in line:
            continue
        start = line.index(needle) + 1
        remainder = line[start:]
        if "`" not in remainder:
            return None
        payload = remainder.split("`", 1)[0]
        return payload.split("=", 1)[1]
    return None


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    required_paths = (
        PHASE2_CLOSURE,
        DOCS_README,
        TESTS_README,
        SCRIPTS_README,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    if issues:
        return issues

    closure_text = read_text(root, PHASE2_CLOSURE)
    docs_text = read_text(root, DOCS_README)
    tests_text = read_text(root, TESTS_README)
    scripts_text = read_text(root, SCRIPTS_README)

    assignment_value = extract_assignment_value(closure_text, "PHASE2_NEXT_SAFE_STEP")
    if assignment_value is None:
        issues.append(("MISSING_ASSIGNMENT", "PHASE2_NEXT_SAFE_STEP"))
    elif assignment_value != EXPECTED_NEXT_SAFE_STEP:
        issues.append(("NEXT_SAFE_STEP_ASSIGNMENT_MISMATCH", "PHASE2_NEXT_SAFE_STEP"))

    for snippet in REQUIRED_NOTE_SNIPPETS:
        if snippet not in closure_text:
            issues.append(("MISSING_CLOSURE_SNIPPET", snippet))

    for rel in REQUIRED_PATH_REFERENCES:
        if rel not in closure_text:
            issues.append(("MISSING_SHARED_PATH_REFERENCE", rel))

    for rel in FORBIDDEN_LANE_ESCALATIONS:
        if (assignment_value is not None and rel in assignment_value) or rel in closure_text:
            issues.append(("HELPER_LOCAL_ESCALATION_IN_NEXT_STEP", rel))

    if "Tests-root reviewer prompt:" not in tests_text:
        issues.append(("MISSING_TESTS_REVIEWER_PROMPT", TESTS_README))
    if "keep the bounded Phase 2 reminder" not in tests_text:
        issues.append(("MISSING_TESTS_SHARED_REMINDER", TESTS_README))

    if "Phase 2 flow" not in scripts_text:
        issues.append(("MISSING_SCRIPTS_PHASE2_FLOW", SCRIPTS_README))
    if "if future work widens the installer or direct cross-route packet" not in scripts_text:
        issues.append(("MISSING_SCRIPTS_REFRESH_GUIDANCE", SCRIPTS_README))

    for hint in REQUIRED_SHARED_PACKET_HINTS:
        if hint not in docs_text:
            issues.append(("MISSING_DOCS_SHARED_PACKET_HINT", hint))

    if "the active Phase 2 packet is still the directly readable current Phase 2 closure note" not in docs_text:
        issues.append(("MISSING_DOCS_PHASE2_PACKET_GUIDANCE", DOCS_README))

    if count_exact_lines(
        closure_text,
        f"- `PHASE2_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP}`",
    ) != 1:
        issues.append(("DUPLICATE_OR_MISSING_NEXT_STEP_LINE", "PHASE2_NEXT_SAFE_STEP"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_NEXT_SAFE_STEP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    closure_lines = (
        "# Phase 2 Closure",
        "",
        "## Next Step",
        "",
        "The next bounded same-lane follow-through is to keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again. If current `master` reopens the shared backlog first, start with one smallest truthfulness repair in `Documentation/zigux/README.md`, `zigux/tests/README.md`, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes instead of sending this shared packet back through the already-covered toolchain-pinning-versus-`phase2-fixdep` comparison.",
        "",
        f"- `PHASE2_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP}`",
        "",
    )
    docs_lines = (
        "# Zigux",
        "",
        "## Phase 2 notes",
        "",
        "the active Phase 2 packet is still the directly readable current Phase 2 closure note together with the returned scripts-root and tests-root reminder surfaces",
        "",
    )
    tests_lines = (
        "# zigux/tests",
        "",
        "## Phase 2 review packet",
        "",
        "keep the bounded Phase 2 reminder aligned with the shared closure note and reminder surfaces",
        "",
        "Tests-root reviewer prompt:",
        "- Does the bounded Phase 2 reminder stay aligned?",
        "",
    )
    scripts_lines = (
        "# scripts/zigux",
        "",
        "## Phase 2",
        "",
        "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker and closure-side validator packet",
        "- if future work widens the installer or direct cross-route packet, update this reminder packet only after rereading those direct current-`master` surfaces together with the live toolchain policy, manifest-backed kconfig fixture roster, the fixture-backed Phase 2 tool packet, and shipped make-wrapper packet so the scripts-root summary stays aligned with the now-returned Phase 2 evidence",
        "",
    )

    write_text(root, PHASE2_CLOSURE, "\n".join(closure_lines))
    write_text(root, DOCS_README, "\n".join(docs_lines))
    write_text(root, TESTS_README, "\n".join(tests_lines))
    write_text(root, SCRIPTS_README, "\n".join(scripts_lines))


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_next_safe_step_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        write_text(root, PHASE2_CLOSURE, "# drifted\n")
        expect_issue(root, ("MISSING_ASSIGNMENT", "PHASE2_NEXT_SAFE_STEP"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            PHASE2_CLOSURE,
            replace_exact_line(
                read_text(root, PHASE2_CLOSURE),
                f"- `PHASE2_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP}`",
                "- `PHASE2_NEXT_SAFE_STEP=drifted next step`",
            ),
        )
        expect_issue(root, ("NEXT_SAFE_STEP_ASSIGNMENT_MISMATCH", "PHASE2_NEXT_SAFE_STEP"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            PHASE2_CLOSURE,
            replace_exact_line(
                read_text(root, PHASE2_CLOSURE),
                "The next bounded same-lane follow-through is to keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again. If current `master` reopens the shared backlog first, start with one smallest truthfulness repair in `Documentation/zigux/README.md`, `zigux/tests/README.md`, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes instead of sending this shared packet back through the already-covered toolchain-pinning-versus-`phase2-fixdep` comparison.",
                "The next bounded same-lane follow-through is to rewrite scripts/zigux/fixdep.zig directly.",
            ),
        )
        expect_issue(root, ("MISSING_CLOSURE_SNIPPET", REQUIRED_NOTE_SNIPPETS[1]))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            PHASE2_CLOSURE,
            replace_exact_line(
                read_text(root, PHASE2_CLOSURE),
                f"- `PHASE2_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP}`",
                "- `PHASE2_NEXT_SAFE_STEP=rewrite scripts/zigux/fixdep.zig directly`",
            ),
        )
        expect_issue(root, ("HELPER_LOCAL_ESCALATION_IN_NEXT_STEP", "scripts/zigux/fixdep.zig"))
        checks += 1

        build_sample_root(root)
        write_text(root, TESTS_README, "# zigux/tests\n")
        expect_issue(root, ("MISSING_TESTS_REVIEWER_PROMPT", TESTS_README))
        checks += 1

        build_sample_root(root)
        write_text(root, SCRIPTS_README, "# scripts/zigux\n")
        expect_issue(root, ("MISSING_SCRIPTS_PHASE2_FLOW", SCRIPTS_README))
        checks += 1

        build_sample_root(root)
        write_text(root, DOCS_README, "# Zigux\n")
        expect_issue(root, ("MISSING_DOCS_SHARED_PACKET_HINT", "Phase 2 notes"))
        checks += 1

        build_sample_root(root)
        closure_text = read_text(root, PHASE2_CLOSURE)
        duplicated = "\n".join(
            closure_text.splitlines()
            + [f"- `PHASE2_NEXT_SAFE_STEP={EXPECTED_NEXT_SAFE_STEP}`"]
        ) + "\n"
        write_text(root, PHASE2_CLOSURE, duplicated)
        expect_issue(root, ("DUPLICATE_OR_MISSING_NEXT_STEP_LINE", "PHASE2_NEXT_SAFE_STEP"))
        checks += 1

    print("PHASE2_NEXT_SAFE_STEP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_NEXT_SAFE_STEP_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 2 next-safe-step handoff packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a synthetic passing sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_NEXT_SAFE_STEP_PACKET=pass")
    print("PHASE2_NEXT_SAFE_STEP_PACKET_SHARED_PATH_COUNT=2")
    print("PHASE2_NEXT_SAFE_STEP_PACKET_FORBIDDEN_HELPER_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
