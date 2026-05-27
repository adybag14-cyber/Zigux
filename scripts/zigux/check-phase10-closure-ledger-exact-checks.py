#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

LEDGER_PATH = Path("zigux-alpha/PHASE10_CLOSURE_LEDGER.md")
MANIFEST_PATH = Path("zigux/tests/phase10_closure_manifest.json")
CLOSURE_DOC_PATH = Path("Documentation/zigux/phase10-closure-evidence.md")

REQUIRED_PATHS = [LEDGER_PATH, MANIFEST_PATH, CLOSURE_DOC_PATH]

LEDGER_PAIR = re.compile(r"^- `([^=]+)=(.*)`$")

CLOSURE_DOC_MARKERS = [
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-core-packet.py",
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "scripts/zigux/check-phase10-ring-packet.py",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/check-phase10-closure-manifest-counts.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_build.zig",
    "zigux/Makefile",
]


def read_text(root: Path, rel_path: Path) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def parse_ledger_pairs(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        match = LEDGER_PAIR.match(line)
        if match:
            pairs[match.group(1)] = match.group(2)
    return pairs


def collect_missing_paths(root: Path) -> list[str]:
    return [str(rel_path) for rel_path in REQUIRED_PATHS if not (root / rel_path).exists()]


def collect_drift(root: Path) -> list[str]:
    ledger = parse_ledger_pairs(read_text(root, LEDGER_PATH))
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    closure_doc = read_text(root, CLOSURE_DOC_PATH)
    issues: list[str] = []

    manifest_checks = manifest.get("exact_checks", [])
    if not isinstance(manifest_checks, list) or not all(isinstance(item, str) for item in manifest_checks):
        issues.append("manifest:exact_checks_not_string_list")
        manifest_checks = []

    for index, check in enumerate(manifest_checks, start=1):
        key = f"PHASE10_LEDGER_EXACT_CHECK_{index}"
        if ledger.get(key) != check:
            issues.append(f"ledger:{key}:{ledger.get(key, '<missing>')}!={check}")

    unexpected_keys = sorted(
        key for key in ledger if key.startswith("PHASE10_LEDGER_EXACT_CHECK_") and int(key.rsplit("_", 1)[1]) > len(manifest_checks)
    )
    for key in unexpected_keys:
        issues.append(f"ledger:{key}:unexpected={ledger[key]}")

    expected_entrypoints = ",".join(
        [
            "make -C zigux phase10-validate",
            "make -C zigux phase10-test",
            "make -C zigux phase10",
        ]
    )
    if ledger.get("PHASE10_LEDGER_ENTRYPOINTS") != expected_entrypoints:
        issues.append(
            "ledger:PHASE10_LEDGER_ENTRYPOINTS:"
            f"{ledger.get('PHASE10_LEDGER_ENTRYPOINTS', '<missing>')}!={expected_entrypoints}"
        )

    evidence_path = "Documentation/zigux/phase10-closure-evidence.md"
    if ledger.get("PHASE10_LEDGER_EVIDENCE") != evidence_path:
        issues.append(
            "ledger:PHASE10_LEDGER_EVIDENCE:"
            f"{ledger.get('PHASE10_LEDGER_EVIDENCE', '<missing>')}!={evidence_path}"
        )

    manifest_path = "zigux/tests/phase10_closure_manifest.json"
    if ledger.get("PHASE10_LEDGER_MANIFEST") != manifest_path:
        issues.append(
            "ledger:PHASE10_LEDGER_MANIFEST:"
            f"{ledger.get('PHASE10_LEDGER_MANIFEST', '<missing>')}!={manifest_path}"
        )

    provenance = manifest.get("survey_provenance", {})
    lane_keys = provenance.get("lane_keys", {})
    surveyed_commits = provenance.get("surveyed_commits", {})
    for family, lane in lane_keys.items():
        key = f"PHASE10_LEDGER_SURVEY_{family.upper()}_LANE"
        if ledger.get(key) != lane:
            issues.append(f"ledger:{key}:{ledger.get(key, '<missing>')}!={lane}")
    for family, commit in surveyed_commits.items():
        key = f"PHASE10_LEDGER_SURVEY_{family.upper()}_COMMIT"
        if ledger.get(key) != commit:
            issues.append(f"ledger:{key}:{ledger.get(key, '<missing>')}!={commit}")

    for marker in CLOSURE_DOC_MARKERS:
        if marker not in closure_doc:
            issues.append(f"closure:{marker}")

    return issues


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture(root: Path) -> None:
    write_text(
        root / LEDGER_PATH,
        "\n".join(
            [
                "# Phase 10 Closure Ledger",
                "",
                "- `PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md`",
                "- `PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json`",
                "- `PHASE10_LEDGER_ENTRYPOINTS=make -C zigux phase10-validate,make -C zigux phase10-test,make -C zigux phase10`",
                "- `PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01`",
                "- `PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10`",
                "- `PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22`",
                "- `PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11`",
                "- `PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8`",
                "- `PHASE10_LEDGER_SURVEY_RING_COMMIT=0aa2db32bcb1c7065850ee3f66ec119b071fbf5c`",
                "- `PHASE10_LEDGER_SURVEY_INPUT_COMMIT=ee789f026f11a0c5c70ded9a868979cdf4f55393`",
                "- `PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8`",
                "- `PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-bootstrap-route.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/check-phase10-core-packet.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_3=python3 scripts/zigux/check-phase10-shared-freeze-boundary.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-ring-packet.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_5=python3 scripts/zigux/check-phase10-input-packet.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_6=python3 scripts/zigux/check-phase10-mmio-packet.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_7=python3 scripts/zigux/check-phase10-harness-coverage.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_9=python3 scripts/zigux/check-phase10-closure-manifest-counts.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_10=python3 scripts/zigux/validate-phase10.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_11=python3 scripts/zigux/validate-phase10-closure.py`",
                "- `PHASE10_LEDGER_EXACT_CHECK_12=make -C zigux phase10-validate`",
                "- `PHASE10_LEDGER_EXACT_CHECK_13=zig build test --build-file zigux/tests/phase10_build.zig --summary all`",
                "- `PHASE10_LEDGER_EXACT_CHECK_14=make -C zigux phase10-test`",
                "- `PHASE10_LEDGER_EXACT_CHECK_15=make -C zigux phase10`",
                "",
            ]
        ),
    )
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "exact_checks": [
                    "python3 scripts/zigux/check-phase10-bootstrap-route.py",
                    "python3 scripts/zigux/check-phase10-core-packet.py",
                    "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py",
                    "python3 scripts/zigux/check-phase10-ring-packet.py",
                    "python3 scripts/zigux/check-phase10-input-packet.py",
                    "python3 scripts/zigux/check-phase10-mmio-packet.py",
                    "python3 scripts/zigux/check-phase10-harness-coverage.py",
                    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
                    "python3 scripts/zigux/check-phase10-closure-manifest-counts.py",
                    "python3 scripts/zigux/validate-phase10.py",
                    "python3 scripts/zigux/validate-phase10-closure.py",
                    "make -C zigux phase10-validate",
                    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
                    "make -C zigux phase10-test",
                    "make -C zigux phase10",
                ],
                "survey_provenance": {
                    "lane_keys": {
                        "core": "P10-L01",
                        "ring": "P10-L10",
                        "input": "P10-L22",
                        "mmio": "P10-L11",
                    },
                    "surveyed_commits": {
                        "core": "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
                        "ring": "0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
                        "input": "ee789f026f11a0c5c70ded9a868979cdf4f55393",
                        "mmio": "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
                    },
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / CLOSURE_DOC_PATH, "\n".join(CLOSURE_DOC_MARKERS) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase10_ledger_exact_checks_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing = collect_missing_paths(root)
        if missing:
            raise SystemExit(f"phase10-ledger-exact-checks:self-test:missing:{','.join(missing)}")
        drift = collect_drift(root)
        if drift:
            raise SystemExit(f"phase10-ledger-exact-checks:self-test:baseline:{','.join(drift)}")
        cases = 1

        ledger_path = root / LEDGER_PATH
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_EXACT_CHECK_9=python3 scripts/zigux/check-phase10-closure-manifest-counts.py",
                "PHASE10_LEDGER_EXACT_CHECK_9=python3 scripts/zigux/check-phase10-counts.py",
                1,
            ),
            encoding="utf-8",
        )
        drift = collect_drift(root)
        if not any(item.startswith("ledger:PHASE10_LEDGER_EXACT_CHECK_9:") for item in drift):
            raise SystemExit("phase10-ledger-exact-checks:self-test:exact-check-drift")
        cases += 1
        ledger_path.write_text(original_ledger, encoding="utf-8")

        manifest_path = root / MANIFEST_PATH
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(original_manifest)
        manifest["survey_provenance"]["lane_keys"]["ring"] = "P10-L07"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        drift = collect_drift(root)
        if "ledger:PHASE10_LEDGER_SURVEY_RING_LANE:P10-L10!=P10-L07" not in drift:
            raise SystemExit("phase10-ledger-exact-checks:self-test:survey-lane-drift")
        cases += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        closure_path = root / CLOSURE_DOC_PATH
        original_closure = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(
            original_closure.replace("scripts/zigux/check-phase10-harness-coverage.py", "scripts/zigux/check-phase10-missing.py", 1),
            encoding="utf-8",
        )
        drift = collect_drift(root)
        if "closure:scripts/zigux/check-phase10-harness-coverage.py" not in drift:
            raise SystemExit("phase10-ledger-exact-checks:self-test:closure-marker-drift")
        cases += 1
        closure_path.write_text(original_closure, encoding="utf-8")

        ledger_path.unlink()
        missing = collect_missing_paths(root)
        if str(LEDGER_PATH) not in missing:
            raise SystemExit("phase10-ledger-exact-checks:self-test:missing-ledger-not-detected")
        cases += 1

    print("PHASE10_CLOSURE_LEDGER_EXACT_CHECKS_SELF_TEST=pass")
    print(f"PHASE10_CLOSURE_LEDGER_EXACT_CHECKS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 10 closure ledger mirrors the manifest-backed exact-check packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_paths(args.root)
    if missing:
        print("PHASE10_CLOSURE_LEDGER_EXACT_CHECKS=fail")
        print("MISSING_PHASE10_CLOSURE_LEDGER_EXACT_CHECK_PATHS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE10_CLOSURE_LEDGER_EXACT_CHECK_PATHS_END")
        return 1

    drift = collect_drift(args.root)
    if drift:
        print("PHASE10_CLOSURE_LEDGER_EXACT_CHECKS=fail")
        print("PHASE10_CLOSURE_LEDGER_EXACT_CHECK_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE10_CLOSURE_LEDGER_EXACT_CHECK_DRIFT_END")
        return 1

    manifest = json.loads(read_text(args.root, MANIFEST_PATH))
    print("PHASE10_CLOSURE_LEDGER_EXACT_CHECKS=pass")
    print(f"PHASE10_CLOSURE_LEDGER_EXACT_CHECK_COUNT={len(manifest.get('exact_checks', []))}")
    print(f"PHASE10_CLOSURE_LEDGER_SURVEY_PROVENANCE_COUNT={len(manifest.get('survey_provenance', {}).get('lane_keys', {}))}")
    print(f"PHASE10_CLOSURE_LEDGER_CLOSURE_DOC_MARKER_COUNT={len(CLOSURE_DOC_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
