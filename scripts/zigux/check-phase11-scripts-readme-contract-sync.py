#!/usr/bin/env python3
"""Keep the Phase 11 scripts-root reminder gap aligned with the shared contract."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

DEFAULT_ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)
CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

CONTRACT_SKIP_MARKERS = (
    "broader contributor-facing summaries in `scripts/zigux/README.md` still skip that active packet",
    "no `Documentation/zigux/README.md` or `scripts/zigux/README.md` Phase 11 coverage on current `master`",
)

SCRIPTS_README_ACTIVE_MARKERS = (
    "## Phase 11",
    "scripts/zigux/validate-phase11.py",
    "make -C zigux phase11-validate",
    "Documentation/zigux/phase11-shared-replay-contract.md",
)


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def contains_marker(text: str, marker: str) -> bool:
    return normalize_whitespace(marker) in normalize_whitespace(text)


def has_scripts_readme_phase11_packet(text: str) -> bool:
    return all(contains_marker(text, marker) for marker in SCRIPTS_README_ACTIVE_MARKERS)


def has_contract_skip_markers(text: str) -> bool:
    return all(contains_marker(text, marker) for marker in CONTRACT_SKIP_MARKERS)


def run_check(root: Path) -> None:
    contract = read_text(root / CONTRACT_PATH)
    scripts_readme = read_text(root / SCRIPTS_README_PATH)

    scripts_root_carries_phase11 = has_scripts_readme_phase11_packet(scripts_readme)
    contract_claims_scripts_root_gap = has_contract_skip_markers(contract)

    if scripts_root_carries_phase11 and contract_claims_scripts_root_gap:
        raise CheckError(
            "scripts-root README now carries the Phase 11 packet, but the shared contract still claims it skips it"
        )
    if not scripts_root_carries_phase11 and not contract_claims_scripts_root_gap:
        raise CheckError(
            "scripts-root README still skips the Phase 11 packet, but the shared contract no longer records that gap"
        )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, scripts_has_phase11: bool, contract_claims_gap: bool) -> None:
    contract_lines = ["# Phase 11 Shared Replay Contract"]
    if contract_claims_gap:
        contract_lines.extend(CONTRACT_SKIP_MARKERS)

    scripts_lines = ["# scripts/zigux", "", "## Phase 10", "- existing packet"]
    if scripts_has_phase11:
        scripts_lines.extend(
            [
                "",
                "## Phase 11",
                "- `scripts/zigux/validate-phase11.py` keeps the packet explicit",
                "- `make -C zigux phase11-validate` replays the shipped route",
                "- `Documentation/zigux/phase11-shared-replay-contract.md` records the shared contract",
            ]
        )

    write(root / CONTRACT_PATH, "\n".join(contract_lines) + "\n")
    write(root / SCRIPTS_README_PATH, "\n".join(scripts_lines) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_scripts_readme_contract_sync_"))
    try:
        missing_readme_truthful_contract = tmpdir / "missing_readme_truthful_contract"
        build_fixture(
            missing_readme_truthful_contract,
            scripts_has_phase11=False,
            contract_claims_gap=True,
        )
        run_check(missing_readme_truthful_contract)
        case_count = 1

        readme_repaired_contract_repaired = tmpdir / "readme_repaired_contract_repaired"
        build_fixture(
            readme_repaired_contract_repaired,
            scripts_has_phase11=True,
            contract_claims_gap=False,
        )
        run_check(readme_repaired_contract_repaired)
        case_count += 1

        readme_repaired_contract_stale = tmpdir / "readme_repaired_contract_stale"
        build_fixture(
            readme_repaired_contract_stale,
            scripts_has_phase11=True,
            contract_claims_gap=True,
        )
        expect_failure(readme_repaired_contract_stale, "still claims it skips it")
        case_count += 1

        readme_missing_contract_overclaims = tmpdir / "readme_missing_contract_overclaims"
        build_fixture(
            readme_missing_contract_overclaims,
            scripts_has_phase11=False,
            contract_claims_gap=False,
        )
        expect_failure(readme_missing_contract_overclaims, "still skips the Phase 11 packet")
        case_count += 1

        print("PHASE11_SCRIPTS_README_CONTRACT_SYNC_SELF_TEST=pass")
        print(f"PHASE11_SCRIPTS_README_CONTRACT_SYNC_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_SCRIPTS_README_CONTRACT_SYNC=fail: {exc}")
        return 1

    print("PHASE11_SCRIPTS_README_CONTRACT_SYNC=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
