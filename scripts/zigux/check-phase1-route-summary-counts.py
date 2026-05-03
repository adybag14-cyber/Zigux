#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    override = os.environ.get("ZIGUX_PHASE1_ROOT")
    if override:
        return Path(override)
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = repo_root()

REQUIRED_MARKERS = {
    "docs_root_phase1_closure_packet_count": (
        "Documentation/zigux/README.md",
        "- `Documentation/zigux/phase1-closure.md` remains the dedicated closure packet for the bounded host-side `tools/lib/*.zig` helper tranche, and `zigux/tests/fixtures/phase1_helper_manifest.json` plus `zigux/tests/phase1_helpers.zig` keep the closed helper inventory and parity-backed replay surface explicit from the docs root.",
        1,
    ),
    "docs_root_phase1_entrypoints_count": (
        "Documentation/zigux/README.md",
        "- `python3 scripts/zigux/validate-phase1.py`, `python3 scripts/zigux/validate-phase1-closure.py`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` are the current validator-first and replay entrypoints for that bounded host-side helper packet.",
        1,
    ),
    "scripts_root_phase1_validator_first_count": (
        "scripts/zigux/README.md",
        "- `validate-phase1.py` is the validator-first entrypoint for the closed host-helper packet around `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/string.zig`, and `tools/lib/rbtree.zig` plus the bounded supporting helpers and committed `zigux/tests/fixtures/phase1_helpers.json` corpus.",
        1,
    ),
    "scripts_root_phase1_review_hooks_count": (
        "scripts/zigux/README.md",
        "- `check-phase1-parity.py --self-test`, `check-phase1-parity.py`, `check-phase1-bench.py --self-test`, `check-phase1-bench.py`, `validate-phase1-closure.py --self-test`, and `validate-phase1-closure.py` are the bounded fail-closed review hooks around that same closed Phase 1 helper tranche.",
        1,
    ),
}


def read_lines(rel: str) -> list[str]:
    return (ROOT / rel).read_text(encoding="utf-8").splitlines()


def fail(items: list[str]) -> int:
    print("PHASE1_ROUTE_SUMMARY_COUNTS=fail")
    print("MISSING_PHASE1_ROUTE_SUMMARY_COUNTS_START")
    for item in items:
        print(item)
    print("MISSING_PHASE1_ROUTE_SUMMARY_COUNTS_END")
    return 1


def main() -> int:
    missing: list[str] = []
    for label, (rel, marker, expected_count) in REQUIRED_MARKERS.items():
        if not (ROOT / rel).exists():
            missing.append(f"{label}:missing_file:{rel}")
            continue
        actual_count = sum(1 for line in read_lines(rel) if line.strip() == marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")

    if missing:
        return fail(missing)

    print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")
    print(f"PHASE1_ROUTE_SUMMARY_COUNT_TARGETS={len(REQUIRED_MARKERS)}")
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_text(entries: list[str]) -> str:
    return "\n".join(entries) + "\n"


def expect_failure(script: Path, root: Path, expected: str) -> None:
    env = dict(os.environ)
    env["ZIGUX_PHASE1_ROOT"] = str(root)
    code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, str(script)], env)
    if code == 0:
        raise SystemExit(f"phase1-route-summary-self-test:expected_failure:{expected}")


def self_test() -> int:
    docs_markers = [
        REQUIRED_MARKERS["docs_root_phase1_closure_packet_count"][1],
        REQUIRED_MARKERS["docs_root_phase1_entrypoints_count"][1],
    ]
    scripts_markers = [
        REQUIRED_MARKERS["scripts_root_phase1_validator_first_count"][1],
        REQUIRED_MARKERS["scripts_root_phase1_review_hooks_count"][1],
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-route-summary-") as tmp:
        root = Path(tmp)
        script = root / "scripts/zigux/check-phase1-route-summary-counts.py"
        write(script, Path(__file__).read_text(encoding="utf-8"))
        write(root / "Documentation/zigux/README.md", fixture_text(docs_markers))
        write(root / "scripts/zigux/README.md", fixture_text(scripts_markers))

        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, str(script)], env)
        if code != 0:
            print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=fail")
            return 1

        write(root / "Documentation/zigux/README.md", "# Zigux Documentation\n")
        expect_failure(
            script,
            root,
            "docs_root_phase1_closure_packet_count:expected=1:actual=0",
        )
        write(root / "Documentation/zigux/README.md", fixture_text(docs_markers))

        write(
            root / "Documentation/zigux/README.md",
            fixture_text(docs_markers + [docs_markers[0]]),
        )
        expect_failure(
            script,
            root,
            "docs_root_phase1_closure_packet_count:expected=1:actual=2",
        )
        write(root / "Documentation/zigux/README.md", fixture_text(docs_markers))

        write(root / "scripts/zigux/README.md", "# scripts/zigux\n")
        expect_failure(
            script,
            root,
            "scripts_root_phase1_validator_first_count:expected=1:actual=0",
        )
        write(root / "scripts/zigux/README.md", fixture_text(scripts_markers))

        write(
            root / "scripts/zigux/README.md",
            fixture_text(scripts_markers + [scripts_markers[1]]),
        )
        expect_failure(
            script,
            root,
            "scripts_root_phase1_review_hooks_count:expected=1:actual=2",
        )

    print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")
    print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST_CASE_COUNT=5")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())
