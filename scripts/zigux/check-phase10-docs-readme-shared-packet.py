#!/usr/bin/env python3
"""Check that the docs-root Phase 10 summary still matches the shared virtio packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


DOCS_ROOT_README_PATH = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "Phase 10 notes - `Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase10-bootstrap-route.py`",
    "`scripts/zigux/check-phase10-shared-freeze-boundary.py`",
    "`scripts/zigux/check-phase10-ring-packet.py`",
    "`scripts/zigux/check-phase10-input-packet.py`",
    "`scripts/zigux/check-phase10-mmio-packet.py`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`scripts/zigux/validate-phase10.py`",
    "`scripts/zigux/validate-phase10-closure.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/tests/phase10_build.zig`",
    "`zigux/Makefile`",
    "current `master` does materialize `zigux/Makefile`, and its live body now exposes `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`",
    "`python3 scripts/zigux/check-phase10-bootstrap-route.py`",
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
)

FORBIDDEN_MARKERS = (
    "while still treating them as missing-route vocabulary in the docs root",
    "while still treating them as missing direct-readback gaps",
)


def check_docs_root(text: str) -> None:
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing:
        raise SystemExit(
            "phase10 docs-root checker missing markers: " + ", ".join(missing)
        )

    present_forbidden = [marker for marker in FORBIDDEN_MARKERS if marker in text]
    if present_forbidden:
        raise SystemExit(
            "phase10 docs-root checker found forbidden markers: "
            + ", ".join(present_forbidden)
        )


def run_self_test() -> int:
    good = """# Zigux Documentation
Phase 10 notes - `Documentation/zigux/phase10-closure-evidence.md` - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `scripts/zigux/check-phase10-bootstrap-route.py` - `scripts/zigux/check-phase10-shared-freeze-boundary.py` - `scripts/zigux/check-phase10-ring-packet.py` - `scripts/zigux/check-phase10-input-packet.py` - `scripts/zigux/check-phase10-mmio-packet.py` - `scripts/zigux/check-phase10-harness-coverage.py` - `scripts/zigux/check-phase10-tests-readme-core-surfaces.py` - `scripts/zigux/validate-phase10.py` - `scripts/zigux/validate-phase10-closure.py` - `zigux/tests/README.md` - `zigux/tests/phase10_closure_manifest.json` - `zigux/tests/phase10_build.zig` - `zigux/Makefile` keep the bounded Phase 10 docs-root packet explicit.
current `master` does materialize `zigux/Makefile`, and its live body now exposes `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`, so keep that returned file and those returned route names explicit as the shared build gate instead of treating them as missing-route vocabulary in the docs root.
`python3 scripts/zigux/check-phase10-bootstrap-route.py`, `python3 scripts/zigux/check-phase10-shared-freeze-boundary.py`, `python3 scripts/zigux/check-phase10-ring-packet.py`, `python3 scripts/zigux/check-phase10-input-packet.py`, `python3 scripts/zigux/check-phase10-mmio-packet.py`, `python3 scripts/zigux/check-phase10-harness-coverage.py`, `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `python3 scripts/zigux/validate-phase10-closure.py`, `make -C zigux phase10-validate`, `zig build test --build-file zigux/tests/phase10_build.zig --summary all`, `make -C zigux phase10-test`, and `make -C zigux phase10` replay the bounded current Phase 10 packet.
"""
    check_docs_root(good.replace("instead of treating them as missing-route vocabulary in the docs root.", ""))

    bad_missing_marker = good.replace("`scripts/zigux/check-phase10-harness-coverage.py` - ", "", 1)
    try:
        check_docs_root(bad_missing_marker)
    except SystemExit as exc:
        assert "harness-coverage" in str(exc)
    else:
        raise AssertionError("expected missing harness-coverage marker failure")

    bad_missing_route = good.replace("`make -C zigux phase10-test`", "`make -C zigux phase10-test-missing`", 1)
    try:
        check_docs_root(bad_missing_route)
    except SystemExit as exc:
        assert "phase10-test" in str(exc)
    else:
        raise AssertionError("expected missing phase10-test marker failure")

    bad_forbidden = good.replace(
        "instead of treating them as missing-route vocabulary in the docs root.",
        "while still treating them as missing-route vocabulary in the docs root.",
        1,
    )
    try:
        check_docs_root(bad_forbidden)
    except SystemExit as exc:
        assert "forbidden" in str(exc)
    else:
        raise AssertionError("expected forbidden stale-route wording failure")

    print("PHASE10_DOCS_ROOT_CHECKER_SELF_TEST=pass")
    print("PHASE10_DOCS_ROOT_CHECKER_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--docs-root-readme", type=Path, default=DOCS_ROOT_README_PATH)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_docs_root(args.docs_root_readme.read_text(encoding="utf-8"))
    print("PHASE10_DOCS_ROOT_CHECK=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
