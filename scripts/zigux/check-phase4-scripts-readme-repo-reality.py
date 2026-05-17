#!/usr/bin/env python3
"""Guard the Phase 4 scripts-root rollback reminder against repo drift."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

README = Path("scripts/zigux/README.md")

DIRECT_READBACK_PACKET = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
)

RETURNED_BROADER_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
)

DEDICATED_LOCAL_PERF_PACKET = (
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/check-phase4-perf-baseline-values.py",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
)

RETURNED_DIFF_PACKET = (
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
)

REQUIRED_MARKERS = (
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces, and current `master` now also materializes the broader validator and lab-matrix packet plus the dedicated local-only perf packet again",
    "keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the broader-packet warning, the roadmap-backed `atomic64_diff` repo-reality wording, and the pending shared-CI perf-promotion posture explicit",
    "are directly readable again on current `master`, so treat them as the returned broader validator and lab-matrix companions",
    "keep the dedicated local-only perf packet explicit beside the shared rollback packet while shared-CI perf promotion stays pending and intentionally separate from the narrower exact-readback target set",
    "are also directly readable on current `master`, so keep those roadmap-backed differential-gate and helper-backed rollback replays framed as current validator-backed companions",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod explicit as coordination owners",
    "keep the parked kprobe plus parked `test_fsmount` reminder packet framed as adjacent last-known packet members",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def require_paths_listed(text: str, paths: tuple[str, ...], label: str) -> None:
    missing = [path for path in paths if f"`{path}`" not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required path markers: {missing}")


def require_repo_reality(root: Path) -> None:
    missing_direct = [path for path in DIRECT_READBACK_PACKET if not (root / path).exists()]
    if missing_direct:
        raise RuntimeError(
            "direct-readback packet no longer matches the current tree: "
            + ", ".join(missing_direct)
        )

    missing_returned = [
        path for path in RETURNED_BROADER_PACKET if not (root / path).exists()
    ]
    if missing_returned:
        raise RuntimeError(
            "returned broader validator packet no longer matches the current tree: "
            + ", ".join(missing_returned)
        )

    missing_perf = [
        path for path in DEDICATED_LOCAL_PERF_PACKET if not (root / path).exists()
    ]
    if missing_perf:
        raise RuntimeError(
            "dedicated local-only perf packet no longer matches the current tree: "
            + ", ".join(missing_perf)
        )

    missing_diff = [path for path in RETURNED_DIFF_PACKET if not (root / path).exists()]
    if missing_diff:
        raise RuntimeError(
            "returned differential and helper-backed replay packet no longer matches the current tree: "
            + ", ".join(missing_diff)
        )


def check(root: Path) -> None:
    readme = read(root, README)
    require(readme, REQUIRED_MARKERS, README.as_posix())
    require_paths_listed(readme, DIRECT_READBACK_PACKET, README.as_posix())
    require_paths_listed(readme, RETURNED_BROADER_PACKET, README.as_posix())
    require_paths_listed(readme, DEDICATED_LOCAL_PERF_PACKET, README.as_posix())
    require_paths_listed(readme, RETURNED_DIFF_PACKET, README.as_posix())
    require_repo_reality(root)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    write(
        root / README,
        """# scripts/zigux

## Phase 4

- Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces, and current `master` now also materializes the broader validator and lab-matrix packet plus the dedicated local-only perf packet again, so this note should stay aligned with present readback while still keeping the perf packet intentionally separate from the narrower exact-readback target set
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the broader-packet warning, the roadmap-backed `atomic64_diff` repo-reality wording, and the pending shared-CI perf-promotion posture explicit, and this scripts-root note should mirror that same present-current-master posture
- `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/validate-phase4.py`, and `zigux/tests/phase4_build.zig` are directly readable again on current `master`, so treat them as the returned broader validator and lab-matrix companions instead of leaving them in the missing-packet bucket
- `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-baseline-values.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` keep the dedicated local-only perf packet explicit beside the shared rollback packet while shared-CI perf promotion stays pending and intentionally separate from the narrower exact-readback target set
- `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` are also directly readable on current `master`, so keep those roadmap-backed differential-gate and helper-backed rollback replays framed as current validator-backed companions instead of as repo-reality gaps here
- keep the dedicated local-only perf packet and any broader shared-CI perf-promotion decision owned by the Validation and Perf Team, keep the ABI and Runtime Team plus Shared Subsystems Pod explicit as coordination owners for any wider promotion call, and keep the parked kprobe plus parked `test_fsmount` reminder packet framed as adjacent last-known packet members instead of reopening this shared scripts-root note into unrelated Phase 4 packet churn
""",
    )

    for packet in (
        DIRECT_READBACK_PACKET,
        RETURNED_BROADER_PACKET,
        DEDICATED_LOCAL_PERF_PACKET,
        RETURNED_DIFF_PACKET,
    ):
        for path in packet:
            write(root / path, "# present packet member\n")


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-scripts-readme-") as tmp:
        root = Path(tmp)
        fixture_root(root)
        check(root)
        cases += 1

        write(
            root / README,
            read(root, README).replace(
                "host-side artifact-diff contract references",
                "host-side contract references",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected artifact-diff wording drift to fail")

        fixture_root(root)
        (root / Path(DIRECT_READBACK_PACKET[-1])).unlink()
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected missing direct packet member to fail")

        fixture_root(root)
        (root / Path(RETURNED_BROADER_PACKET[0])).unlink()
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected missing returned broader packet member to fail")

        fixture_root(root)
        (root / Path(DEDICATED_LOCAL_PERF_PACKET[0])).unlink()
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected missing local-only perf packet member to fail")

        fixture_root(root)
        (root / Path(RETURNED_DIFF_PACKET[0])).unlink()
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected missing returned diff packet member to fail")

        fixture_root(root)
        write(
            root / README,
            read(root, README).replace(
                "keep the ABI and Runtime Team plus Shared Subsystems Pod explicit as coordination owners",
                "keep the coordination owners explicit",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected owner-split drift to fail")

    print("PHASE4_SCRIPTS_README_REPO_REALITY_SELF_TEST=pass")
    print(f"PHASE4_SCRIPTS_README_REPO_REALITY_SELF_TEST_CASES={cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0

    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_SCRIPTS_README_REPO_REALITY=fail: {exc}", file=sys.stderr)
        return 1

    print("PHASE4_SCRIPTS_README_REPO_REALITY=pass")
    print(
        f"PHASE4_SCRIPTS_README_REPO_REALITY_DIRECT_PACKET_MEMBERS={len(DIRECT_READBACK_PACKET)}"
    )
    print(
        "PHASE4_SCRIPTS_README_REPO_REALITY_RETURNED_BROADER_PACKET_MEMBERS="
        f"{len(RETURNED_BROADER_PACKET)}"
    )
    print(
        "PHASE4_SCRIPTS_README_REPO_REALITY_DEDICATED_LOCAL_PERF_PACKET_MEMBERS="
        f"{len(DEDICATED_LOCAL_PERF_PACKET)}"
    )
    print(
        "PHASE4_SCRIPTS_README_REPO_REALITY_RETURNED_DIFF_PACKET_MEMBERS="
        f"{len(RETURNED_DIFF_PACKET)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
