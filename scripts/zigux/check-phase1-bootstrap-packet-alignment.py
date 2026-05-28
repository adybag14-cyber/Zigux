#!/usr/bin/env python3
"""Guard the Phase 1 bootstrap packet against reminder drift."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_host_tools_smoke.zig",
)

WORKFLOW_RUNS = (
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-string-review-packet.py",
    "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "python3 scripts/zigux/check-phase1-bench.py --self-test",
    "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "python3 scripts/zigux/validate-phase1-closure.py",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

VALIDATOR_MARKERS = (
    'PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")',
    'PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")',
    'DOCS_ROOT_REL = Path("Documentation/zigux/README.md")',
    'REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")',
    'SCRIPTS_README_REL = Path("scripts/zigux/README.md")',
    'TESTS_README_REL = Path("zigux/tests/README.md")',
    'TESTS_BUILD_REL = Path("zigux/tests/build.zig")',
    'PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")',
    'WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")',
    'MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")',
    'ZIGUX_MAKEFILE_REL = Path("zigux/Makefile")',
)

SURFACE_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "PHASE1_STATUS=parked",
        "PHASE1_CURRENT_REMINDER_PACKET=",
        "scripts/zigux/validate-phase1-closure.py",
        "zigux/tests/phase1_host_tools_smoke.zig",
    ),
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md": (
        "Phase 1 helper follow-up stays parked on shared replay",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    ),
    "Documentation/zigux/README.md": (
        "scripts/zigux/validate-phase1-closure.py",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/Makefile",
    ),
    "Documentation/zigux/review-checklist.md": (
        "closed Phase 1 host-tools packet",
        "scripts/zigux/validate-phase1-closure.py",
        "zig build test --build-file zigux/tests/build.zig",
    ),
    "scripts/zigux/README.md": (
        "validate-phase1-closure.py",
        "check-phase1-shared-reminder-packet.py",
        "check-phase1-bench.py",
    ),
    "zigux/tests/README.md": (
        "phase1_host_tools_smoke.zig",
        "phase1_helper_manifest.json",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    "zigux/tests/build.zig": ("phase1-host-tools-smoke", "phase1_host_tools_smoke.zig"),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        '@import("bitmap")',
        '@import("find_bit")',
        '@import("rbtree")',
        '@import("string")',
    ),
    "zigux/Makefile": (
        "phase1-validate:",
        "phase1-test:",
        "phase1-bench:",
        "phase1: phase1-validate phase1-test phase1-bench",
    ),
}

HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)
DIRECT_HELPERS = ("tools/lib/bitmap.zig", "tools/lib/find_bit.zig", "tools/lib/rbtree.zig", "tools/lib/string.zig")


def text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def missing(root: Path) -> dict[str, list[str]]:
    missing_files = [rel for rel in REQUIRED if not (root / rel).is_file()]
    if missing_files:
        return {"missing_files": missing_files}

    issues: dict[str, list[str]] = {
        "surface_markers": [],
        "workflow_runs": [],
        "validator_markers": [],
        "manifest": [],
    }
    for rel, markers in SURFACE_MARKERS.items():
        body = text(root, rel)
        issues["surface_markers"].extend(f"{rel}:{marker}" for marker in markers if marker not in body)
    workflow_runs = {
        line.split("run:", 1)[1].strip()
        for line in text(root, ".github/workflows/zigux-bootstrap.yml").splitlines()
        if line.lstrip().startswith("run:")
    }
    issues["workflow_runs"].extend(run for run in WORKFLOW_RUNS if run not in workflow_runs)
    validator = text(root, "scripts/zigux/validate-phase1-closure.py")
    issues["validator_markers"].extend(marker for marker in VALIDATOR_MARKERS if marker not in validator)

    try:
        manifest = json.loads(text(root, "zigux/tests/fixtures/phase1_helper_manifest.json"))
    except json.JSONDecodeError as exc:
        issues["manifest"].append(f"json:{exc.msg}:line={exc.lineno}:column={exc.colno}")
        return issues
    helpers = manifest.get("helpers")
    direct = manifest.get("direct_anchor_followup_helpers")
    lane_rules = manifest.get("lane_rules")
    if not isinstance(helpers, list):
        issues["manifest"].append("helpers:list")
    else:
        issues["manifest"].extend(f"helpers:{helper}" for helper in HELPERS if helper not in helpers)
    if not isinstance(direct, list):
        issues["manifest"].append("direct_anchor_followup_helpers:list")
    else:
        issues["manifest"].extend(f"direct_anchor_followup_helpers:{helper}" for helper in DIRECT_HELPERS if helper not in direct)
    if not isinstance(lane_rules, dict):
        issues["manifest"].append("lane_rules:dict")
    else:
        for key in ("rule_summary", "anti_overlap_rule"):
            value = lane_rules.get(key)
            if not isinstance(value, str) or "Phase 1" not in value:
                issues["manifest"].append(f"lane_rules:{key}")
    return issues


def any_issues(issues: dict[str, list[str]]) -> bool:
    return any(values for values in issues.values())


def report(issues: dict[str, list[str]]) -> None:
    for label, values in issues.items():
        if values:
            print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_{label.upper()}_START")
            print("\n".join(values))
            print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_{label.upper()}_END")


def write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_sample(root: Path) -> None:
    for rel in REQUIRED:
        write(root, rel, "sample\n")
    write(root, ".github/workflows/zigux-bootstrap.yml", "\n".join(f"run: {run}" for run in WORKFLOW_RUNS) + "\n")
    write(root, "scripts/zigux/validate-phase1-closure.py", "\n".join(VALIDATOR_MARKERS) + "\n")
    for rel, markers in SURFACE_MARKERS.items():
        write(root, rel, "\n".join(markers) + "\n")
    write(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(
            {
                "phase": "Phase 1",
                "helpers": list(HELPERS),
                "direct_anchor_followup_helpers": list(DIRECT_HELPERS),
                "lane_rules": {
                    "rule_summary": "Phase 1 helper follow-up stays parked on shared replay.",
                    "anti_overlap_rule": "Do not reopen Phase 1 by batching helpers.",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        sample = Path(tmp) / "sample"
        write_sample(sample)
        if any_issues(missing(sample)):
            report(missing(sample))
            raise SystemExit("generated sample should pass")
        broken_workflow = Path(tmp) / "broken-workflow"
        shutil.copytree(sample, broken_workflow)
        workflow = broken_workflow / ".github/workflows/zigux-bootstrap.yml"
        workflow.write_text(workflow.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/validate-phase1-closure.py\n", ""), encoding="utf-8")
        if not missing(broken_workflow)["workflow_runs"]:
            raise SystemExit("removed workflow route should fail")
        broken_manifest = Path(tmp) / "broken-manifest"
        shutil.copytree(sample, broken_manifest)
        manifest_path = broken_manifest / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["direct_anchor_followup_helpers"].remove("tools/lib/rbtree.zig")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        if not missing(broken_manifest)["manifest"]:
            raise SystemExit("removed manifest helper should fail")
        broken_surface = Path(tmp) / "broken-surface"
        shutil.copytree(sample, broken_surface)
        (broken_surface / "Documentation/zigux/review-checklist.md").write_text("closed Phase 2 packet\n", encoding="utf-8")
        if not missing(broken_surface)["surface_markers"]:
            raise SystemExit("removed review-checklist marker should fail")
    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST=pass")
    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST_CASE_COUNT=4")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.write_sample_root:
        write_sample(Path(args.write_sample_root).resolve())
        return
    root = Path(args.root).resolve() if args.root else ROOT
    issues = missing(root)
    if any_issues(issues):
        report(issues)
        raise SystemExit(1)
    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=pass")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED)}")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_WORKFLOW_ROUTE_COUNT={len(WORKFLOW_RUNS)}")


if __name__ == "__main__":
    main()
