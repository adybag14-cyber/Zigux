#!/usr/bin/env python3
"""Guard the Phase 1 string roadmap-ledger gap survey against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
GAP_NOTE_REL = Path("Documentation/zigux/phase1-string-roadmap-ledger-gap.md")

REQUIRED_EXACT_LINES = {
    "roadmap_target": "- `ROADMAP_PHASE1_TARGET=tools/lib/string.zig`",
    "ledger_target": "- `LEDGER_COMMIT6_TARGET=tools/lib/string.zig`",
    "public_tree_gap": "- current public-tree readback of `tools/lib` shows `cmdline.zig` as the only directly readable `.zig` helper in that directory in this environment",
    "authenticated_gap": "- authenticated contents reads for `tools/lib/string.zig` on current `master` return missing",
    "reminder_surface_gap": "- current Phase 1 reminder surfaces still name `tools/lib/string.zig` as a direct-anchor helper in `Documentation/zigux/phase1-host-helper-lane-sequencing.md` and `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "lane_decision": "- treat `tools/lib/string.zig` as a roadmap-and-ledger target that is not currently materialized on readable `master`",
    "proof_boundary": "- do not present the current string manifest anchors as direct helper-file proof while `tools/lib/string.zig` remains unreadable on current `master`",
    "next_step": "- align the current Phase 1 reminder packet one surface at a time so it distinguishes the roadmap-ledger string target from direct current-master helper evidence",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == line)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_gap_failures(root: Path) -> list[str]:
    gap_note_path = root / GAP_NOTE_REL
    if not gap_note_path.exists():
        return [f"missing_file:{GAP_NOTE_REL.as_posix()}"]

    gap_note_text = load_text(root, GAP_NOTE_REL)
    missing: list[str] = []
    for label, line in REQUIRED_EXACT_LINES.items():
        missing.extend(require_exact_line(gap_note_text, f"gap_note:{label}", line))
    return missing


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_gap_note_text() -> str:
    ordered_lines = [
        REQUIRED_EXACT_LINES["roadmap_target"],
        REQUIRED_EXACT_LINES["ledger_target"],
        REQUIRED_EXACT_LINES["public_tree_gap"],
        REQUIRED_EXACT_LINES["authenticated_gap"],
        REQUIRED_EXACT_LINES["reminder_surface_gap"],
        REQUIRED_EXACT_LINES["lane_decision"],
        REQUIRED_EXACT_LINES["proof_boundary"],
        REQUIRED_EXACT_LINES["next_step"],
    ]
    return (
        "# Phase 1 String Roadmap-Ledger Gap\n\n"
        "## Roadmap And Ledger Expectation\n\n"
        + "\n".join(ordered_lines[:2])
        + "\n\n## Current Repo Reality\n\n"
        + "\n".join(ordered_lines[2:5])
        + "\n\n## Current Lane Decision\n\n"
        + "\n".join(ordered_lines[5:7])
        + "\n\n## Next Bounded Step\n\n"
        + ordered_lines[7]
        + "\n"
    )


def build_sample_repo(root: Path) -> None:
    write_file(root, GAP_NOTE_REL, sample_gap_note_text())


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str]] = [("success", None, "none")]
    for label, line in REQUIRED_EXACT_LINES.items():
        cases.append((f"missing_{label}", line, "remove"))
        cases.append((f"duplicate_{label}", line, "duplicate"))

    for name, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-gap-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if needle:
                target = root / GAP_NOTE_REL
                text = target.read_text(encoding="utf-8")
                if operation == "remove":
                    target.write_text(text.replace(needle + "\n", "", 1), encoding="utf-8")
                elif operation == "duplicate":
                    target.write_text(text.replace(needle, needle + "\n" + needle, 1), encoding="utf-8")

            missing = collect_gap_failures(root)
            if name == "success":
                if missing:
                    print(f"self-test:{name}:unexpected_failures")
                    for item in missing:
                        print(item)
                    return 1
                continue

            if not missing:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_gap_failures(repo_root(args.root))
    if missing:
        for item in missing:
            print(item)
        return 1

    print("phase1-string-roadmap-ledger-gap:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
