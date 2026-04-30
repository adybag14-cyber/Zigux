#!/usr/bin/env python3
from __future__ import annotations

import argparse

from validate_phase3_core import ROOT, discover_phase3_slices, select_slices, validate_slices
from validate_phase3_header_binding_markers import (
    run_self_test as run_header_binding_marker_self_test,
    validate_header_binding_markers,
)
from validate_phase3_selftest import run_self_test


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 3 slice catalog and metadata.")
    parser.add_argument("--slug", action="append", default=[], help="Only validate the named Phase 3 slug. Repeat to validate more than one.")
    parser.add_argument("--check-artifact-diff", action="store_true", help="Also validate the generated Current Phase 3 use section.")
    parser.add_argument("--check-build-smoke", action="store_true", help="Also run focused Zig build smoke checks for the selected Phase 3 slices.")
    parser.add_argument("--check-slug-sanity", action="store_true", help="Also audit discovered Phase 3 slugs for naming drift.")
    parser.add_argument("--skip-obsolete-wrapper-check", action="store_true", help="Skip the stale wrapper-file scan.")
    parser.add_argument("--zig", help="Explicit zig executable path for --check-build-smoke runs.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator checks.")
    args = parser.parse_args()

    if args.self_test:
        result = run_self_test()
        if result != 0:
            return result
        return run_header_binding_marker_self_test()

    slices = select_slices(discover_phase3_slices(), args.slug)
    if not slices:
        raise SystemExit("no Phase 3 slugs discovered")

    issues = validate_header_binding_markers(ROOT)
    issues.extend(
        validate_slices(
            ROOT,
            slices,
            check_artifact_diff=args.check_artifact_diff,
            check_build_smoke=args.check_build_smoke,
            check_slug_sanity=args.check_slug_sanity,
            check_all_wrappers=not args.skip_obsolete_wrapper_check,
            zig_path=args.zig,
        )
    )
    if issues:
        print("PHASE3_VALIDATION=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_VALIDATION=pass")
    print("PHASE3_VALIDATED_SLUGS=" + ",".join(entry.slug for entry in slices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
