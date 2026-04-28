#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
ARTIFACT_DIFF_PATH = ROOT / "scripts/zigux/artifact_diff.py"
TRACKED_PATHS = [
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "tools/lib/bpf/zigux_segments/manifest.json",
]


def file_digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load_surveyed_commit() -> str:
    manifest = json.loads((ROOT / TRACKED_PATHS[0]).read_text(encoding="utf-8"))
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or len(surveyed_commit) != 40:
        raise SystemExit("invalid Phase 12 libbpf surveyed_commit")
    return surveyed_commit


def render_snapshot() -> dict[str, object]:
    surveyed_commit = load_surveyed_commit()
    files = [file_digest(ROOT / rel_path) for rel_path in TRACKED_PATHS]
    return {
        "lane_key": "P12-L17",
        "phase": "Phase 12",
        "surveyed_commit": surveyed_commit,
        "tracked_file_count": len(files),
        "files": files,
    }


def main() -> int:
    first = render_snapshot()
    second = render_snapshot()
    if first != second:
        print("PHASE12_LIBBPF_SNAPSHOT=fail")
        print("PHASE12_LIBBPF_REPEAT_RUN=drift")
        return 1

    rendered = json.dumps(first, indent=2) + "\n"
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_") as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / "phase12_libbpf_snapshot.json"
        actual_path.write_text(rendered, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ARTIFACT_DIFF_PATH),
                "--mode",
                "json",
                str(FIXTURE_PATH),
                str(actual_path),
            ],
            check=False,
            text=True,
            capture_output=True,
        )

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    if result.returncode != 0:
        print("PHASE12_LIBBPF_SNAPSHOT=fail")
        print("PHASE12_LIBBPF_REPEAT_RUN=stable")
        return result.returncode

    print("PHASE12_LIBBPF_SNAPSHOT=pass")
    print("PHASE12_LIBBPF_REPEAT_RUN=stable")
    print(f"PHASE12_LIBBPF_TRACKED_FILE_COUNT={first['tracked_file_count']}")
    print(
        "PHASE12_LIBBPF_SNAPSHOT_SHA256="
        + hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
