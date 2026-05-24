#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("Documentation/zigux/README.md")

PHASE9_MARKER = "Phase 9 notes - "
PHASE10_MARKER = "Phase 10 notes - "
PHASE12_MARKER = "Phase 12 notes - "

REQUIRED_MARKERS = (
    "Phase 10 notes - `Documentation/zigux/phase10-closure-evidence.md` - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/tests/phase10_build.zig` keep the shared Phase 10 docs-root reminder packet explicit through the closure note",
    "the current docs-root Phase 10 reminder packet should stay parked on `Documentation/zigux/phase10-closure-evidence.md`",
    "current `master` directly serves `drivers/virtio/virtio_input_probe_preflight.zig` and `zigux/tests/phase10_virtio_input_probe_preflight.zig`",
    "`python3 scripts/zigux/check-phase10-harness-coverage.py`, `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` replay the bounded current Phase 10 docs-root reminder packet",
)

REQUIRED_PATHS = (
    Path("Documentation/zigux/phase10-closure-evidence.md"),
    Path("Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("zigux/tests/README.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/check-phase10-harness-coverage.py"),
    Path("scripts/zigux/check-phase10-tests-readme-core-surfaces.py"),
    Path("zigux/tests/phase10_closure_manifest.json"),
    Path("zigux/tests/phase10_build.zig"),
    Path("drivers/virtio/virtio_input_probe_preflight.zig"),
    Path("zigux/tests/phase10_virtio_input_probe_preflight.zig"),
)


def check_phase10_notes(root: Path) -> list[str]:
    text = (root / README_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"missing marker: {marker}")

    phase9_pos = text.find(PHASE9_MARKER)
    phase10_pos = text.find(PHASE10_MARKER)
    phase12_pos = text.find(PHASE12_MARKER)
    if min(phase9_pos, phase10_pos, phase12_pos) == -1:
        errors.append("missing Phase 9, Phase 10, or Phase 12 boundary marker")
    elif not (phase9_pos < phase10_pos < phase12_pos):
        errors.append("phase order mismatch: expected Phase 9 -> Phase 10 -> Phase 12")

    phase10_count = text.count(PHASE10_MARKER)
    if phase10_count != 1:
        errors.append(f"unexpected Phase 10 marker count: {phase10_count}")

    for path in REQUIRED_PATHS:
        if not (root / path).exists():
            errors.append(f"missing linked path: {path.as_posix()}")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# Zigux Documentation

Phase 9 notes - `Documentation/zigux/freeze-map.md` keep the shared Phase 9 reminder packet honest.

Phase 10 notes - `Documentation/zigux/phase10-closure-evidence.md` - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `scripts/zigux/README.md` - `scripts/zigux/check-phase10-harness-coverage.py` - `scripts/zigux/check-phase10-tests-readme-core-surfaces.py` - `zigux/tests/phase10_closure_manifest.json` - `zigux/tests/phase10_build.zig` keep the shared Phase 10 docs-root reminder packet explicit through the closure note, the lane-sequencing owner map, the shared review and tests-root reminder surfaces, the dedicated scripts-root reminder, the paired harness and tests-readme guards, and the shared closure manifest plus build-route packet instead of leaving the docs root narrower than the current shared closure gate on `master`.
* the current docs-root Phase 10 reminder packet should stay parked on `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/tests/phase10_build.zig` so the docs root matches the same shared Phase 10 reminder packet already carried by the closure note, lane-sequencing note, tests-root review companion, scripts-root reminder, closure manifest, and shared build route.
* current `master` directly serves `drivers/virtio/virtio_input_probe_preflight.zig` and `zigux/tests/phase10_virtio_input_probe_preflight.zig` beside the broader shared closure packet, so keep that bounded input preflight reminder explicit here instead of leaving the docs root to jump from the Phase 9 study-only packet straight to the Phase 12 release packet.
* `python3 scripts/zigux/check-phase10-harness-coverage.py`, `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` replay the bounded current Phase 10 docs-root reminder packet while risky transport stays parked behind the shared closure manifest and its lane-local follow-through notes.

Phase 12 notes - `Documentation/zigux/phase12-release-sequencing.md` keep the bounded Phase 12 docs-root packet explicit.
"""


def _materialize_current_like_root(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())
    for path in REQUIRED_PATHS:
        _write(root / path, "")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase10_notes_") as tmp_dir:
        root = Path(tmp_dir)
        _materialize_current_like_root(root)

        errors = check_phase10_notes(root)
        if errors:
            raise AssertionError(f"baseline Phase 10 fixture should pass: {errors}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(PHASE10_MARKER, "Phase Ten notes - ", 1))
        errors = check_phase10_notes(root)
        if "missing Phase 9, Phase 10, or Phase 12 boundary marker" not in errors:
            raise AssertionError(f"expected missing Phase 10 heading error, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`scripts/zigux/check-phase10-harness-coverage.py`",
                "`scripts/zigux/check-phase10-other.py`",
            ),
        )
        errors = check_phase10_notes(root)
        if not any(error.startswith("missing marker: `scripts/zigux/check-phase10-harness-coverage.py`") for error in errors):
            raise AssertionError(f"expected missing harness marker, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Phase 9 notes - `Documentation/zigux/freeze-map.md` keep the shared Phase 9 reminder packet honest.\n\n"
                "Phase 10 notes - ",
                "Phase 10 notes - ",
                1,
            ).replace(
                "\n\nPhase 12 notes - `Documentation/zigux/phase12-release-sequencing.md` keep the bounded Phase 12 docs-root packet explicit.",
                "\n\nPhase 9 notes - `Documentation/zigux/freeze-map.md` keep the shared Phase 9 reminder packet honest."
                "\n\nPhase 12 notes - `Documentation/zigux/phase12-release-sequencing.md` keep the bounded Phase 12 docs-root packet explicit.",
                1,
            ),
        )
        errors = check_phase10_notes(root)
        if "phase order mismatch: expected Phase 9 -> Phase 10 -> Phase 12" not in errors:
            raise AssertionError(f"expected order mismatch, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`drivers/virtio/virtio_input_probe_preflight.zig` and `zigux/tests/phase10_virtio_input_probe_preflight.zig`",
                "`drivers/virtio/virtio_input_probe_preflight.zig`",
                1,
            ),
        )
        errors = check_phase10_notes(root)
        if not any("zigux/tests/phase10_virtio_input_probe_preflight.zig" in error for error in errors):
            raise AssertionError(f"expected missing preflight marker, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        (root / Path("zigux/tests/phase10_build.zig")).unlink()
        errors = check_phase10_notes(root)
        if "missing linked path: zigux/tests/phase10_build.zig" not in errors:
            raise AssertionError(f"expected missing linked path error, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(PHASE10_MARKER, f"{PHASE10_MARKER}\n{PHASE10_MARKER}", 1))
        errors = check_phase10_notes(root)
        if "unexpected Phase 10 marker count: 2" not in errors:
            raise AssertionError(f"expected duplicate heading error, got: {errors}")
        _materialize_current_like_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`python3 scripts/zigux/check-phase10-harness-coverage.py`, `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`",
                "`python3 scripts/zigux/check-phase10-harness-coverage.py`, `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, and `make -C zigux phase10-validate`",
                1,
            ),
        )
        errors = check_phase10_notes(root)
        if not any(error.startswith("missing marker: `python3 scripts/zigux/check-phase10-harness-coverage.py`") for error in errors):
            raise AssertionError(f"expected missing validation-route marker, got: {errors}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE10_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE10_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 docs-root Phase 10 reminder packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic docs-root Phase 10 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_phase10_notes(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE10_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE10_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE10_NOTES_SECTION_ORDER=Phase9->Phase10->Phase12")
    print(f"LANE01_DOCS_ROOT_PHASE10_NOTES_LINKED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
