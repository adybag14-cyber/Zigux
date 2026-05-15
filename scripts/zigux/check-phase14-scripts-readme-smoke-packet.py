#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=scripts_readme_smoke_packet

Fail-closed checker for the scripts-root summary of the shared Phase 14 smoke
packet.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=scripts_readme_smoke_packet"
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
REQUIRED_MARKERS = [
    "Phase 14 flow",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`Documentation/zigux/phase14-core-boundary-traceability.md`",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/freeze-map.md`",
    "`scripts/zigux/validate-phase14.py`",
    "`scripts/zigux/check-phase14-docs-root-smoke-summary.py`",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`",
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`zigux/tests/phase14_build.zig`",
    "`make -C zigux phase14-validate`",
    "`make -C zigux phase14-smoke`",
    "`make -C zigux phase14-test`",
    "`make -C zigux phase14`",
    "shared Phase 14 smoke packet",
    "focused smoke-shard replay contract",
    "stay-in-C boundary",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    path = root / SCRIPTS_README_PATH
    if not path.exists():
        errors.append(f"missing file: {SCRIPTS_README_PATH.as_posix()}")
    else:
        require_exact_count(
            errors,
            SCRIPTS_README_PATH.as_posix(),
            read_text(path),
            REQUIRED_MARKERS,
        )

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")
    return errors


def good_scripts_readme_text() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "Phase 14 flow",
            "- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
            "- `Documentation/zigux/phase14-core-boundary-traceability.md`",
            "- `Documentation/zigux/phase14-release-boundary-survey.md`",
            "- `Documentation/zigux/review-checklist.md`",
            "- `Documentation/zigux/freeze-map.md`",
            "- `scripts/zigux/validate-phase14.py`",
            "- `scripts/zigux/check-phase14-docs-root-smoke-summary.py`",
            "- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`",
            "- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
            "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
            "- `zigux/tests/phase14_build.zig`",
            "- `make -C zigux phase14-validate`",
            "- `make -C zigux phase14-smoke`",
            "- `make -C zigux phase14-test`",
            "- `make -C zigux phase14`",
            "- shared Phase 14 smoke packet",
            "- focused smoke-shard replay contract",
            "- stay-in-C boundary",
        ]
    ) + "\n"


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if any(needle in error for error in errors):
        return
    print(label, file=sys.stderr)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())

        if errors := check(root, source_text=MARKER):
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        write_text(
            root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "`Documentation/zigux/phase14-core-boundary-traceability.md`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "`Documentation/zigux/phase14-core-boundary-traceability.md`",
            "self-test expected missing traceability marker failure",
        )
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())

        write_text(
            root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "`Documentation/zigux/phase14-core-boundary-traceability.md`\n",
                "`Documentation/zigux/phase14-core-boundary-traceability.md`\n"
                "`Documentation/zigux/phase14-core-boundary-traceability.md`\n",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "`Documentation/zigux/phase14-core-boundary-traceability.md`",
            "self-test expected duplicate traceability marker failure",
        )
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())

        write_text(
            root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`",
            "self-test expected missing tests-readme checker marker failure",
        )
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())

        write_text(
            root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "`make -C zigux phase14-smoke`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "`make -C zigux phase14-smoke`",
            "self-test expected missing smoke-route marker failure",
        )
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())

        write_text(
            root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "`zigux/tests/phase14_build.zig`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "`zigux/tests/phase14_build.zig`",
            "self-test expected missing build marker failure",
        )
        write_text(root / SCRIPTS_README_PATH, good_scripts_readme_text())

        write_text(
            root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                "shared Phase 14 smoke packet\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(root, source_text=MARKER),
            "shared Phase 14 smoke packet",
            "self-test expected missing shared-packet summary marker failure",
        )

        expect_contains(
            check(root, source_text="PHASE14_CHECK_PACKET=broken_marker"),
            "checker marker missing from checker source",
            "self-test expected checker-source marker failure",
        )

    print("PHASE14_SCRIPTS_README_SMOKE_PACKET_SELF_TEST=pass")
    print(
        "PHASE14_SCRIPTS_README_SMOKE_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_MARKERS)}"
    )
    print("PHASE14_SCRIPTS_README_SMOKE_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("phase14 scripts-readme smoke packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
