#!/usr/bin/env python3
"""Guard the current Phase 1 reminder packet's Makefile posture."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_PRESENT_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-validate",
    "phase2",
    "phase3-validate",
    "phase3",
    "phase3-export-uapi-layout-test",
    "phase6-base64-test",
    "phase6-base64-perf",
    "phase6-bsearch-test",
    "phase6-checksum-test",
    "phase6-checksum-perf",
    "phase6-hexdump-review",
    "phase6-hexdump-test",
    "phase6-hexdump-perf",
    "phase8-validate",
    "phase8-exec-cmd-test",
    "phase8-help-kallsyms-test",
    "phase8-kallsyms-test",
    "phase8-libbpf-segments-test",
    "phase8-file-path-handle-bridge-test",
    "phase8-perf-buffer-poll-test",
    "phase8-test",
    "phase10-validate",
    "phase10-test",
    "phase10",
    "phase12-smoke",
    "phase12-test",
    "phase12",
)

OPTIONAL_PHONY_ONLY_ROUTES = (
    "phase8-help-test",
    "phase8",
)

REQUIRED_ABSENT_ROUTES = (
    "phase1-validate",
    "phase1-test",
    "phase1-bench",
    "phase1",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def parse_phony_routes(text: str) -> set[str]:
    phony: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith(".PHONY:"):
            continue
        _, routes = line.split(":", 1)
        phony.update(route for route in routes.split() if route)
    return phony


def parse_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for raw_line in text.splitlines():
        if not raw_line or raw_line.startswith((" ", "\t", "#")):
            continue
        if ":" not in raw_line:
            continue
        name, _ = raw_line.split(":", 1)
        target = name.strip()
        if not target or target.startswith(".PHONY"):
            continue
        if " " in target:
            continue
        targets.add(target)
    return targets


def collect_failures(root: Path) -> list[str]:
    makefile_path = root / MAKEFILE_REL
    if not makefile_path.exists():
        return [f"missing_file:{MAKEFILE_REL.as_posix()}"]

    text = load_text(root, MAKEFILE_REL)
    phony_routes = parse_phony_routes(text)
    targets = parse_targets(text)
    failures: list[str] = []

    for route in REQUIRED_PRESENT_ROUTES:
        if route not in phony_routes:
            failures.append(f"missing_phony:{route}")
        if route not in targets:
            failures.append(f"missing_target:{route}")

    for route in REQUIRED_ABSENT_ROUTES:
        if route in phony_routes:
            failures.append(f"unexpected_phony:{route}")
        if route in targets:
            failures.append(f"unexpected_target:{route}")

    return failures


def collect_phony_only_routes(root: Path) -> list[str]:
    text = load_text(root, MAKEFILE_REL)
    phony_routes = parse_phony_routes(text)
    targets = parse_targets(text)
    return [route for route in OPTIONAL_PHONY_ONLY_ROUTES if route in phony_routes and route not in targets]


def make_fixture_text() -> str:
    lines = [
        "PYTHON ?= python3",
        "ZIG ?= zig",
        ".PHONY: " + " ".join(REQUIRED_PRESENT_ROUTES + OPTIONAL_PHONY_ONLY_ROUTES),
        "",
    ]
    for route in REQUIRED_PRESENT_ROUTES:
        lines.append(f"{route}:")
        lines.append("\t@true")
        lines.append("")
    return "\n".join(lines)


def run_self_test() -> int:
    cases = (
        ("baseline", None, True),
        ("missing_present_phony", lambda text: text.replace("phase8-test ", "", 1), False),
        (
            "missing_present_target",
            lambda text: text.replace("phase10-test:\n\t@true\n\n", "", 1),
            False,
        ),
        (
            "unexpected_phase1_target",
            lambda text: text + "phase1:\n\t@true\n",
            False,
        ),
        (
            "unexpected_phase1_phony",
            lambda text: text.replace(
                ".PHONY: ",
                ".PHONY: phase1-validate ",
                1,
            ),
            False,
        ),
    )

    for name, mutate, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-makefile-routes-") as tmp:
            root = Path(tmp)
            makefile_path = root / MAKEFILE_REL
            makefile_path.parent.mkdir(parents=True, exist_ok=True)
            text = make_fixture_text()
            if mutate is not None:
                text = mutate(text)
            makefile_path.write_text(text, encoding="utf-8")
            ok = not collect_failures(root)
            if ok != expect_ok:
                print(f"phase1-makefile-routes-self-test:{name}:unexpected")
                return 1

    print("PHASE1_MAKEFILE_ROUTES_SELF_TEST=pass")
    print(f"PHASE1_MAKEFILE_ROUTES_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_MAKEFILE_ROUTE_SURVEY=pass")
    print(f"PHASE1_MAKEFILE_ROUTE_COUNT={len(REQUIRED_PRESENT_ROUTES)}")
    print(f"PHASE1_MAKEFILE_PHASE1_ABSENT_COUNT={len(REQUIRED_ABSENT_ROUTES)}")
    phony_only_routes = collect_phony_only_routes(root)
    print(
        "PHASE1_MAKEFILE_PHONY_ONLY_ROUTES="
        + (",".join(phony_only_routes) if phony_only_routes else "none")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
