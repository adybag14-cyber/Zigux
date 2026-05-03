#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
REQUIRED_TOOLING_FILES = (
    "scripts/zigux/check-phase3-build-roots.py",
    "scripts/zigux/check-phase3-canonical-survey-manifest.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-tooling-packet.py",
    "scripts/zigux/check-phase3-validation-flow.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate_phase3_core.py",
    "scripts/zigux/validate_phase3_selftest.py",
)


def validate(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_REL
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"missing_manifest:{MANIFEST_REL}"]
    except json.JSONDecodeError as exc:
        return [f"invalid_manifest_json:{MANIFEST_REL}:{exc}"]

    files = manifest.get("files")
    if not isinstance(files, list):
        return [f"missing_manifest_files:{MANIFEST_REL}"]

    issues: list[str] = []
    listed = {entry for entry in files if isinstance(entry, str)}
    for rel in REQUIRED_TOOLING_FILES:
        if rel not in listed:
            issues.append(f"missing_tooling_file:{rel}")
    for rel in REQUIRED_TOOLING_FILES:
        if rel in listed and not (root / rel).exists():
            issues.append(f"missing_repo_file:{rel}")
    return issues


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_tooling_packet_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        manifest_path = root / MANIFEST_REL

        for rel in REQUIRED_TOOLING_FILES:
            _write(root / rel, "# stub\n")

        _write(
            manifest_path,
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": list(REQUIRED_TOOLING_FILES),
                    "file_count": len(REQUIRED_TOOLING_FILES),
                },
                indent=2,
            )
            + "\n",
        )

        issues = validate(root)
        if issues:
            raise SystemExit("phase3-tooling-packet-self-test:baseline_failed:" + ",".join(issues))

        broken_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        broken_manifest["files"] = [rel for rel in REQUIRED_TOOLING_FILES if rel != REQUIRED_TOOLING_FILES[0]]
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        issues = validate(root)
        expected = f"missing_tooling_file:{REQUIRED_TOOLING_FILES[0]}"
        if issues != [expected]:
            raise SystemExit(
                "phase3-tooling-packet-self-test:missing_manifest_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        broken_manifest["files"] = list(REQUIRED_TOOLING_FILES)
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        (root / REQUIRED_TOOLING_FILES[-1]).unlink()
        issues = validate(root)
        expected = f"missing_repo_file:{REQUIRED_TOOLING_FILES[-1]}"
        if issues != [expected]:
            raise SystemExit(
                "phase3-tooling-packet-self-test:missing_repo_file_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

    print("PHASE3_TOOLING_PACKET_SELF_TEST=pass")
    print("PHASE3_TOOLING_PACKET_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 3 manifest aligned with the live repo-tooling packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_TOOLING_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_TOOLING_PACKET=pass")
    print(f"PHASE3_TOOLING_PACKET_FILE_COUNT={len(REQUIRED_TOOLING_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
