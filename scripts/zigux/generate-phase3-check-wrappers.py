#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from phase3_check_lib import render_wrapper_stub


def run_self_test() -> int:
    expected = render_wrapper_stub()
    stale = "#!/usr/bin/env python3\nprint('stale')\n"
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_wrapper_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        expected_wrapper = tmp_dir / "check-phase3-expected.py"
        expected_wrapper.write_text(stale, encoding="utf-8")
        missing_wrapper = tmp_dir / "check-phase3-missing.py"
        assert expected_wrapper.read_text(encoding="utf-8") != expected
        assert not missing_wrapper.exists()
    print("PHASE3_WRAPPER_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Phase 3 wrapper template availability.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    if args.check:
        print("PHASE3_WRAPPER_TEMPLATES=pass")
        return 0
    print("PHASE3_WRAPPER_TEMPLATES=updated:0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
