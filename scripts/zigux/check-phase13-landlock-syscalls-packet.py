#!/usr/bin/env python3
"""Fail-closed checker for the Phase 13 Landlock syscalls helper packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "Documentation/zigux/phase13-landlock-syscalls-slice.md": (
        "# Phase 13 Landlock Syscalls Slice",
        "keeps `landlock_create_ruleset()` reviewable around the ABI-version query branch",
        "keeps one planning-only `landlock_restrict_self()` helper explicit",
        "keeps `landlock_add_rule()` reviewable around ruleset-fd presence",
        "`security/landlock/syscalls.zig`, this slice note, and `Documentation/zigux/phase13-landlock-syscalls-governance.md` are materialized on current `master`, while `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps",
        "This slice does not claim anonymous-fd creation internals beyond the bounded install planner handoff, live fd ownership, live path imports, live credential replacement, thread synchronization side effects, domain merges as shipped behavior, or live syscall enforcement",
    ),
    "Documentation/zigux/phase13-landlock-syscalls-governance.md": (
        "# Phase 13 Landlock Syscalls Governance",
        "Current `master` now materializes `security/landlock/syscalls.zig` as a helper-local starter",
        "Current `master` does not materialize the older direct syscall survey or replay companions through:",
        "- `Documentation/zigux/phase13-landlock-syscalls-survey.md`",
        "- `zigux/tests/phase13_landlock_syscalls.zig`",
        "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "- `zigux/tests/phase13_landlock_syscalls_manifest.json`",
        "Keep this packet parked unless a future lane can add another equally bounded planner.",
    ),
    "Documentation/zigux/phase13-landlock-syscalls-survey-gap.md": (
        "# Phase 13 Landlock Syscalls Survey Gap",
        "The remaining gaps are unchanged and stay outside this bounded helper-local step:",
        "- `Documentation/zigux/phase13-landlock-syscalls-survey.md`",
        "- `zigux/tests/phase13_landlock_syscalls.zig`",
        "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "- `zigux/tests/phase13_landlock_syscalls_manifest.json`",
        "- `zigux/tests/phase13_build.zig`",
        "Do not widen this note into anonymous-inode internals, live FD installation, credential mutation, or domain state.",
    ),
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md": (
        "`landlock/syscalls` owns the narrower syscall governance, slice, helper starter, and helper-local survey-gap packet",
        "`Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`",
    ),
    "Documentation/zigux/phase13-roadmap-traceability.md": (
        "`security/landlock/syscalls.c`: mapped through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, and `security/landlock/syscalls.zig`.",
        "Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` framed as repo-reality gaps until current `master` materializes them again.",
        "- `zigux/tests/phase13_landlock_syscalls.zig`",
        "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "- `zigux/tests/phase13_landlock_syscalls_manifest.json`",
        "- live `landlock/syscalls` file-descriptor installation, credential replacement, ruleset-state ownership, and full syscall enforcement",
    ),
    "security/landlock/syscalls.zig": (
        'pub const ModuleDescriptor = struct {',
        '.provides_create_ruleset_planning = true',
        '.provides_restrict_self_planning = true',
        '.provides_add_rule_planning = true',
        '.provides_ruleset_fd_install_planning = true',
        '.provides_ruleset_fd_stub_planning = true',
        '.provides_ruleset_release_planning = true',
        '.touches_live_fd_installation = false',
        '.touches_live_cred_replacement = false',
        'pub fn planLandlockCreateRuleset(request: CreateRulesetSyscallRequest) !CreateRulesetSyscallPlan {',
        'pub fn planLandlockRestrictSelf(request: RestrictSelfRequest) !RestrictSelfPlan {',
        'pub fn planLandlockAddRule(request: AddRuleSyscallRequest) !AddRuleSyscallPlan {',
        'pub fn planInstallRulesetFd(request: RulesetFdInstallRequest) !RulesetFdInstallPlan {',
        'pub fn planRulesetFdStub(request: RulesetFdStubRequest) !RulesetFdStubPlan {',
        'pub fn planFopRulesetRelease(request: RulesetReleaseRequest) !RulesetReleasePlan {',
    ),
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase13-landlock-syscalls-slice.md": (
        "This slice claims live syscall enforcement.",
    ),
    "Documentation/zigux/phase13-landlock-syscalls-governance.md": (
        "Keep this packet parked unless a future lane can add live syscall enforcement.",
    ),
    "Documentation/zigux/phase13-roadmap-traceability.md": (
        "treat the blocked `make -C zigux phase13-validate` or `make -C zigux phase13` names as the stable shared handle",
    ),
    "security/landlock/syscalls.zig": (
        '.touches_live_fd_installation = true',
        '.touches_live_cred_replacement = true',
    ),
}


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.exists():
        raise FileNotFoundError(relpath)
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    all_paths = sorted(set(REQUIRED_MARKERS) | set(FORBIDDEN_MARKERS))

    for relpath in all_paths:
        try:
            text = read_text(root, relpath)
        except FileNotFoundError:
            issues.append(f"missing_file:{relpath}")
            continue

        for marker in REQUIRED_MARKERS.get(relpath, ()):
            if marker not in text:
                issues.append(f"missing_marker:{relpath}:{marker}")
        for marker in FORBIDDEN_MARKERS.get(relpath, ()):
            if marker in text:
                issues.append(f"forbidden_marker:{relpath}:{marker}")

    return issues


def emit_failure(issues: list[str]) -> int:
    print("PHASE13_LANDLOCK_SYSCALLS_PACKET=fail")
    print("PHASE13_LANDLOCK_SYSCALLS_PACKET_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_LANDLOCK_SYSCALLS_PACKET_ISSUES_END")
    return 1


def populate_fixture(root: Path) -> None:
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")


+def run_self_test() -> int:
+    tempdir = Path(tempfile.mkdtemp(prefix="phase13-landlock-syscalls-packet-"))
+    checks_run = 0
+    try:
+        populate_fixture(tempdir)
+        issues = collect_issues(tempdir)
+        if issues:
+            raise SystemExit(f"fixture tree should pass but failed: {issues!r}")
+        checks_run += 1
+
+        target = tempdir / "Documentation/zigux/phase13-landlock-syscalls-slice.md"
+        target.write_text(
+            target.read_text(encoding="utf-8").replace(
+                "keeps one planning-only `landlock_restrict_self()` helper explicit\n",
+                "",
+                1,
+            ),
+            encoding="utf-8",
+        )
+        issues = collect_issues(tempdir)
+        expected = (
+            "missing_marker:Documentation/zigux/phase13-landlock-syscalls-slice.md:"
+            "keeps one planning-only `landlock_restrict_self()` helper explicit"
+        )
+        if expected not in issues:
+            raise SystemExit(f"expected failure not found: {expected!r} actual={issues!r}")
+        populate_fixture(tempdir)
+        checks_run += 1
+
+        target = tempdir / "Documentation/zigux/phase13-landlock-syscalls-governance.md"
+        target.write_text(
+            target.read_text(encoding="utf-8")
+            + "Keep this packet parked unless a future lane can add live syscall enforcement.\n",
+            encoding="utf-8",
+        )
+        issues = collect_issues(tempdir)
+        expected = (
+            "forbidden_marker:Documentation/zigux/phase13-landlock-syscalls-governance.md:"
+            "Keep this packet parked unless a future lane can add live syscall enforcement."
+        )
+        if expected not in issues:
+            raise SystemExit(f"expected failure not found: {expected!r} actual={issues!r}")
+        populate_fixture(tempdir)
+        checks_run += 1
+
+        target = tempdir / "Documentation/zigux/phase13-roadmap-traceability.md"
+        target.write_text(
+            target.read_text(encoding="utf-8").replace(
+                "- `zigux/tests/phase13_landlock_syscalls_manifest.json`\n",
+                "",
+                1,
+            ),
+            encoding="utf-8",
+        )
+        issues = collect_issues(tempdir)
+        expected = (
+            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:"
+            "- `zigux/tests/phase13_landlock_syscalls_manifest.json`"
+        )
+        if expected not in issues:
+            raise SystemExit(f"expected failure not found: {expected!r} actual={issues!r}")
+        populate_fixture(tempdir)
+        checks_run += 1
+
+        target = tempdir / "security/landlock/syscalls.zig"
+        target.write_text(
+            target.read_text(encoding="utf-8").replace(
+                ".touches_live_cred_replacement = false\n",
+                ".touches_live_cred_replacement = true\n",
+                1,
+            ),
+            encoding="utf-8",
+        )
+        issues = collect_issues(tempdir)
+        expected = (
+            "forbidden_marker:security/landlock/syscalls.zig:.touches_live_cred_replacement = true"
+        )
+        if expected not in issues:
+            raise SystemExit(f"expected failure not found: {expected!r} actual={issues!r}")
+        populate_fixture(tempdir)
+        checks_run += 1
+
+        target = tempdir / "security/landlock/syscalls.zig"
+        target.write_text(
+            target.read_text(encoding="utf-8").replace(
+                "pub fn planInstallRulesetFd(request: RulesetFdInstallRequest) !RulesetFdInstallPlan {\n",
+                "",
+                1,
+            ),
+            encoding="utf-8",
+        )
+        issues = collect_issues(tempdir)
+        expected = (
+            "missing_marker:security/landlock/syscalls.zig:"
+            "pub fn planInstallRulesetFd(request: RulesetFdInstallRequest) !RulesetFdInstallPlan {"
+        )
+        if expected not in issues:
+            raise SystemExit(f"expected failure not found: {expected!r} actual={issues!r}")
+        checks_run += 1
+
+        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST=pass")
+        print(f"PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
+        return 0
+    finally:
+        shutil.rmtree(tempdir, ignore_errors=True)
+
+
 def main() -> int:
     parser = argparse.ArgumentParser(
         description="Validate the Phase 13 Landlock syscalls helper packet and its repo-reality gap discipline."
     )
     parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to validate")
+    parser.add_argument("--self-test", action="store_true", help="Run the built-in fixture self-test")
     args = parser.parse_args()
 
+    if args.self_test:
+        return run_self_test()
+
     issues = collect_issues(args.root)
     if issues:
         return emit_failure(issues)
 
     print("PHASE13_LANDLOCK_SYSCALLS_PACKET=pass")
@@ -173,6 +259,6 @@ def main() -> int:
     )
     return 0
 
 
 if __name__ == "__main__":
     raise SystemExit(main())
