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

MISSING_BROADER_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
)

REQUIRED_MARKERS = (
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces",
    "keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the broader-packet warning, and the pending shared-CI perf-promotion posture explicit",
    "authenticated contents reads on current `master` still return missing for",
    "keep the dedicated local-only perf packet and any broader shared-CI perf-promotion decision owned by the Validation and Perf Team",
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

    present_broader = [path for path in MISSING_BROADER_PACKET if (root / path).exists()]
    if present_broader:
        raise RuntimeError(
            "broader packet entries are now present and the scripts-root reminder must be narrowed: "
            + ", ".join(present_broader)
        )


def check(root: Path) -> None:
    readme = read(root, README)
    require(readme, REQUIRED_MARKERS, README.as_posix())
    require_paths_listed(readme, DIRECT_READBACK_PACKET, README.as_posix())
    require_paths_listed(readme, MISSING_BROADER_PACKET, README.as_posix())
    require_repo_reality(root)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    write(
        root / README,
        """# scripts/zigux

## Phase 4

- Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, and local-only perf packet is currently a repo-reality gap on `master`, so this note should stay aligned with the direct-readback warning instead of treating that older packet as freshly present
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the broader-packet warning, and the pending shared-CI perf-promotion posture explicit, and this scripts-root note should mirror that same present-current-master posture
- authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`, so treat those broader validator, lab-matrix, and local-only perf surfaces as historical packet members or stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` provenance until a same-lane republish makes them directly readable again
- keep the dedicated local-only perf packet and any broader shared-CI perf-promotion decision owned by the Validation and Perf Team, keep the ABI and Runtime Team plus Shared Subsystems Pod explicit as coordination owners for any wider promotion call, and keep the parked kprobe plus parked `test_fsmount` reminder packet framed as adjacent last-known packet members instead of reopening this shared scripts-root note into broader Phase 4 republish work
""",
    )

    for path in DIRECT_READBACK_PACKET:
        write(root / path, "# present direct packet member\n")


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
        write(root / Path(MISSING_BROADER_PACKET[0]), "# broader packet returned\n")
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected returned broader packet member to fail")

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
        f"PHASE4_SCRIPTS_README_REPO_REALITY_MISSING_BROADER_MEMBERS={len(MISSING_BROADER_PACKET)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
