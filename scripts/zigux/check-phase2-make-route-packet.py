#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


def default_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in (here.parent, *here.parents):
        if (candidate / ".github/workflows/zigux-bootstrap.yml").is_file() and (
            candidate / "zigux/Makefile"
        ).is_file():
            return candidate
    return here.parent


ROOT = default_root()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
PHASE2_BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
TESTS_README = Path("zigux/tests/README.md")

ROUTE_COMMANDS = (
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

WORKFLOW_REQUIRED_LINES = (
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

MAKEFILE_REQUIRED_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-kconfig:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

VALIDATOR_REQUIRED_SNIPPETS = (
    '"scripts/zigux/check-phase2-kbuild-routes.py",',
    '"scripts/zigux/check-phase2-required-make-routes.py",',
    '"scripts/zigux/check-phase2-artifact-tools-manifest.py",',
    '"zigux/Makefile",',
    '"run: make -C zigux phase2-toolchain",',
    '"run: make -C zigux phase2-tools",',
    '"run: make -C zigux phase2-kconfig",',
    '"run: make -C zigux phase2-cross",',
    '"run: make -C zigux phase2-genksyms",',
    '"run: make -C zigux phase2-fixdep",',
    '"run: make -C zigux phase2-validate",',
)

CLOSURE_REQUIRED_MARKERS = (
    "- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`",
    "- `python3 scripts/zigux/check-phase2-required-make-routes.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-required-make-routes.py`",
    "the shipped `zigux/Makefile` wrappers",
)

BOOTSTRAP_NOTES_REQUIRED_MARKERS = (
    "names `phase2-toolchain`, `phase2-validate`, and `phase2-cross` as the required Linux-style make routes when those routes are rematerialized",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
)

TESTS_README_REQUIRED_MARKERS = (
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "Keep the current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`",
    "scripts/zigux/check-phase2-required-make-routes.py",
)

REQUIRED_FILES = (
    WORKFLOW,
    MAKEFILE,
    VALIDATE_PHASE2,
    PHASE2_CLOSURE,
    PHASE2_BOOTSTRAP_NOTES,
    TESTS_README,
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"required file missing: {rel.as_posix()}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[str]:
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)
    validate_text = read_text(root, VALIDATE_PHASE2)
    closure_text = read_text(root, PHASE2_CLOSURE)
    bootstrap_notes_text = read_text(root, PHASE2_BOOTSTRAP_NOTES)
    tests_readme_text = read_text(root, TESTS_README)

    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            issues.append(f"missing_file:{rel.as_posix()}")

    phony_targets: set[str] = set()
    for line in makefile_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            phony_targets.update(token for token in suffix.strip().split() if token)
    for route in ("phase2-toolchain", "phase2-tools", "phase2-kconfig", "phase2-cross", "phase2-genksyms", "phase2-fixdep", "phase2-validate", "phase2"):
        if route not in phony_targets:
            issues.append(f"missing_phony_target:{route}")

    for marker in MAKEFILE_REQUIRED_LINES:
        count = count_exact_line(makefile_text, marker)
        if count == 0:
            issues.append(f"missing_makefile_line:{marker}")
        elif count != 1:
            issues.append(f"duplicate_makefile_line:{marker}:count={count}")

    for marker in WORKFLOW_REQUIRED_LINES:
        count = count_exact_line(workflow_text, marker)
        if count == 0:
            issues.append(f"missing_workflow_line:{marker}")
        elif count != 1:
            issues.append(f"duplicate_workflow_line:{marker}:count={count}")

    for marker in VALIDATOR_REQUIRED_SNIPPETS:
        if marker not in validate_text:
            issues.append(f"missing_validator_snippet:{marker}")

    for marker in CLOSURE_REQUIRED_MARKERS:
        if marker not in closure_text:
            issues.append(f"missing_closure_marker:{marker}")

    for marker in BOOTSTRAP_NOTES_REQUIRED_MARKERS:
        if marker not in bootstrap_notes_text:
            issues.append(f"missing_bootstrap_notes_marker:{marker}")

    for marker in TESTS_README_REQUIRED_MARKERS:
        if marker not in tests_readme_text:
            issues.append(f"missing_tests_readme_marker:{marker}")

    route_sentence = ", ".join(ROUTE_COMMANDS[:-1]) + f", and {ROUTE_COMMANDS[-1]}"
    if route_sentence not in tests_readme_text:
        issues.append("missing_tests_readme_route_sentence")

    return issues


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(("name: zigux-bootstrap", *WORKFLOW_REQUIRED_LINES)) + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "ZIGUX_ROOT := ..",
                "ZIG ?= zig",
                "",
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
                *MAKEFILE_REQUIRED_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATE_PHASE2,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                'REQUIRED_PATHS = (',
                '    "scripts/zigux/check-phase2-kbuild-routes.py",',
                '    "scripts/zigux/check-phase2-required-make-routes.py",',
                '    "scripts/zigux/check-phase2-artifact-tools-manifest.py",',
                '    "zigux/Makefile",',
                ')',
                'REQUIRED_WORKFLOW_LINES = (',
                '    "run: make -C zigux phase2-toolchain",',
                '    "run: make -C zigux phase2-tools",',
                '    "run: make -C zigux phase2-kconfig",',
                '    "run: make -C zigux phase2-cross",',
                '    "run: make -C zigux phase2-genksyms",',
                '    "run: make -C zigux phase2-fixdep",',
                '    "run: make -C zigux phase2-validate",',
                ')',
            )
        )
        + "\n",
    )
    write_text(
        root,
        PHASE2_CLOSURE,
        "\n".join(CLOSURE_REQUIRED_MARKERS) + "\n",
    )
    write_text(
        root,
        PHASE2_BOOTSTRAP_NOTES,
        "\n".join(BOOTSTRAP_NOTES_REQUIRED_MARKERS) + "\n",
    )
    write_text(
        root,
        TESTS_README,
        "\n".join(
            (
                *TESTS_README_REQUIRED_MARKERS,
                ", ".join(ROUTE_COMMANDS[:-1]) + f", and {ROUTE_COMMANDS[-1]}",
            )
        )
        + "\n",
    )


def replace_first(text: str, marker: str, replacement: str) -> str:
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_make_route_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, replace_first(read_text(root, MAKEFILE), MAKEFILE_REQUIRED_LINES[0], "phase2-toolchain-disabled:"))
        issues = collect_issues(root)
        assert f"missing_makefile_line:{MAKEFILE_REQUIRED_LINES[0]}" in issues
        case_count += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_first(read_text(root, WORKFLOW), WORKFLOW_REQUIRED_LINES[0], "run: make -C zigux something-else"))
        issues = collect_issues(root)
        assert f"missing_workflow_line:{WORKFLOW_REQUIRED_LINES[0]}" in issues
        case_count += 1

        build_sample_root(root)
        write_text(root, VALIDATE_PHASE2, replace_first(read_text(root, VALIDATE_PHASE2), VALIDATOR_REQUIRED_SNIPPETS[0], '"scripts/zigux/other-checker.py",'))
        issues = collect_issues(root)
        assert f"missing_validator_snippet:{VALIDATOR_REQUIRED_SNIPPETS[0]}" in issues
        case_count += 1

        build_sample_root(root)
        write_text(root, PHASE2_CLOSURE, "phase2 closure drift\n")
        issues = collect_issues(root)
        assert f"missing_closure_marker:{CLOSURE_REQUIRED_MARKERS[0]}" in issues
        case_count += 1

        build_sample_root(root)
        write_text(root, PHASE2_BOOTSTRAP_NOTES, "phase2 notes drift\n")
        issues = collect_issues(root)
        assert f"missing_bootstrap_notes_marker:{BOOTSTRAP_NOTES_REQUIRED_MARKERS[0]}" in issues
        case_count += 1

        build_sample_root(root)
        write_text(root, TESTS_README, "phase2 tests drift\n")
        issues = collect_issues(root)
        assert f"missing_tests_readme_marker:{TESTS_README_REQUIRED_MARKERS[0]}" in issues
        assert "missing_tests_readme_route_sentence" in issues
        case_count += 1

    print("PHASE2_MAKE_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_MAKE_ROUTE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 2 Makefile wrapper packet stays aligned "
            "with the closure note, bootstrap note, tests-root reminder, workflow, "
            "and validator entrypoint."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal passing sample repository tree",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_MAKE_ROUTE_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_MAKE_ROUTE_PACKET=pass")
    print(f"PHASE2_MAKE_ROUTE_PACKET_ROUTE_COUNT={len(ROUTE_COMMANDS)}")
    print(f"PHASE2_MAKE_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_REQUIRED_LINES)}")
    print(f"PHASE2_MAKE_ROUTE_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())