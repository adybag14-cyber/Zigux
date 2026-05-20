#!/usr/bin/env python3
import argparse
import tempfile
from pathlib import Path

WORKFLOW_REL = Path('.github/workflows/zigux-bootstrap.yml')
MAKEFILE_REL = Path('zigux/Makefile')

WORKFLOW_STEPS = [
    ('Run current Phase 2 toolchain make route', 'run: make -C zigux phase2-toolchain'),
    ('Run current Phase 2 tools make route', 'run: make -C zigux phase2-tools'),
    ('Run current Phase 2 kconfig make route', 'run: make -C zigux phase2-kconfig'),
    ('Run current Phase 2 fixdep make route', 'run: make -C zigux phase2-fixdep'),
]

WORKFLOW_BOUNDARY_BEFORE = (
    'Check current Phase 2 toolchain pin-scope packet',
    'run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py',
)
WORKFLOW_BOUNDARY_AFTER = (
    'Self-test current Phase 2 required-make-routes checker',
    'run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test',
)
FORBIDDEN_WORKFLOW_STEPS = [
    ('Run current Phase 2 validate make route', 'run: make -C zigux phase2-validate'),
]

REQUIRED_PHASE2_PHONY_TARGETS = {
    'phase2-toolchain',
    'phase2-tools',
    'phase2-kconfig',
    'phase2-cross',
    'phase2-genksyms',
    'phase2-fixdep',
    'phase2-validate',
    'phase2',
}

MAKEFILE_TARGET_LINES = [
    'phase2-toolchain:',
    'phase2-tools:',
    'phase2-kconfig:',
    'phase2-fixdep:',
    'phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep',
    'phase2: phase2-validate',
]

MAKEFILE_RECIPE_LINES = [
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py',
    'cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig',
    'cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py',
    'cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py',
    '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py',
]

SAMPLE_WORKFLOW = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Check current Phase 2 toolchain pin-scope packet
        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py
      - name: Run current Phase 2 toolchain make route
        run: make -C zigux phase2-toolchain
      - name: Run current Phase 2 tools make route
        run: make -C zigux phase2-tools
      - name: Run current Phase 2 kconfig make route
        run: make -C zigux phase2-kconfig
      - name: Run current Phase 2 fixdep make route
        run: make -C zigux phase2-fixdep
      - name: Self-test current Phase 2 required-make-routes checker
        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test
"""

SAMPLE_MAKEFILE = """PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..

.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3-validate phase3

phase2-toolchain:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py

phase2-tools:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py

phase2-kconfig:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py

phase2-cross:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py

phase2-genksyms:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig

phase2-fixdep:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py

phase2: phase2-validate
"""


class ValidationError(Exception):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError as exc:
        raise ValidationError(f'missing required file: {path}') from exc


def require_once(text: str, snippet: str, label: str) -> int:
    count = text.count(snippet)
    if count != 1:
        raise ValidationError(f'{label} must appear exactly once; found {count}')
    return text.index(snippet)


def require_exact_line(text: str, snippet: str, label: str) -> int:
    lines = text.splitlines()
    matches = [index for index, line in enumerate(lines) if line.strip() == snippet]
    count = len(matches)
    if count != 1:
        raise ValidationError(f'{label} must appear exactly once; found {count}')
    return matches[0]


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('.PHONY:'):
            continue
        _, suffix = stripped.split(':', 1)
        targets.update(token for token in suffix.strip().split() if token)
    return targets


def validate_workflow(workflow_text: str) -> None:
    before_name, before_run = WORKFLOW_BOUNDARY_BEFORE
    after_name, after_run = WORKFLOW_BOUNDARY_AFTER
    before_name_index = require_once(workflow_text, before_name, 'workflow boundary-before step name')
    before_run_index = require_once(workflow_text, before_run, 'workflow boundary-before command')
    if before_name_index > before_run_index:
        raise ValidationError('workflow boundary-before command must follow its step name')

    previous_index = before_run_index
    for step_name, run_line in WORKFLOW_STEPS:
        name_index = require_once(workflow_text, step_name, f'workflow step {step_name}')
        run_index = require_once(workflow_text, run_line, f'workflow command {run_line}')
        if name_index > run_index:
            raise ValidationError(f'workflow command for {step_name} must follow its step name')
        if previous_index >= name_index:
            raise ValidationError(f'workflow step {step_name} is out of order')
        previous_index = run_index

    after_name_index = require_once(workflow_text, after_name, 'workflow boundary-after step name')
    after_run_index = require_once(workflow_text, after_run, 'workflow boundary-after command')
    if after_name_index > after_run_index:
        raise ValidationError('workflow boundary-after command must follow its step name')
    if previous_index >= after_name_index:
        raise ValidationError('workflow make-route packet must finish before the required-make-routes self-test')

    for forbidden_name, forbidden_run in FORBIDDEN_WORKFLOW_STEPS:
        name_count = workflow_text.count(forbidden_name)
        run_count = workflow_text.count(forbidden_run)
        if name_count or run_count:
            raise ValidationError(f'forbidden workflow step still present inside make-route packet: {forbidden_name}')


def validate_makefile(makefile_text: str) -> None:
    if not REQUIRED_PHASE2_PHONY_TARGETS.issubset(phony_targets_present(makefile_text)):
        raise ValidationError('Makefile .PHONY targets must include the current Phase 2 route set')
    for line in MAKEFILE_TARGET_LINES:
        require_exact_line(makefile_text, line, f'Makefile target line {line}')
    for line in MAKEFILE_RECIPE_LINES:
        require_exact_line(makefile_text, line, f'Makefile recipe line {line}')


def validate_root(root: Path) -> None:
    workflow_text = read_text(root / WORKFLOW_REL)
    makefile_text = read_text(root / MAKEFILE_REL)
    validate_workflow(workflow_text)
    validate_makefile(makefile_text)


def write_sample_root(root: Path) -> None:
    workflow_path = root / WORKFLOW_REL
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(SAMPLE_WORKFLOW, encoding='utf-8')

    makefile_path = root / MAKEFILE_REL
    makefile_path.parent.mkdir(parents=True, exist_ok=True)
    makefile_path.write_text(SAMPLE_MAKEFILE, encoding='utf-8')


def run_self_test() -> int:
    case_count = 0

    def expect_pass(mutator=None) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix='lane03_make_route_pass_') as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            if mutator is not None:
                mutator(root)
            validate_root(root)
            case_count += 1

    def expect_fail(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix='lane03_make_route_fail_') as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                validate_root(root)
            except ValidationError as exc:
                if expected_substring not in str(exc):
                    raise AssertionError(f'expected {expected_substring!r} in {exc!r}') from exc
                case_count += 1
                return
            raise AssertionError('expected ValidationError')

    expect_pass()
    expect_fail(
        lambda root: (root / WORKFLOW_REL).write_text(
            read_text(root / WORKFLOW_REL).replace(
                'run: make -C zigux phase2-tools\n',
                '',
            ),
            encoding='utf-8',
        ),
        'workflow command run: make -C zigux phase2-tools must appear exactly once',
    )
    expect_fail(
        lambda root: (root / WORKFLOW_REL).write_text(
            read_text(root / WORKFLOW_REL).replace(
                '      - name: Self-test current Phase 2 required-make-routes checker\n'
                '        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test\n',
                '      - name: Run current Phase 2 validate make route\n'
                '        run: make -C zigux phase2-validate\n'
                '      - name: Self-test current Phase 2 required-make-routes checker\n'
                '        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test\n',
            ),
            encoding='utf-8',
        ),
        'forbidden workflow step still present inside make-route packet: Run current Phase 2 validate make route',
    )
    expect_fail(
        lambda root: (root / WORKFLOW_REL).write_text(
            read_text(root / WORKFLOW_REL).replace(
                '      - name: Run current Phase 2 fixdep make route\n'
                '        run: make -C zigux phase2-fixdep\n'
                '      - name: Self-test current Phase 2 required-make-routes checker\n'
                '        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test\n',
                '      - name: Self-test current Phase 2 required-make-routes checker\n'
                '        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test\n'
                '      - name: Run current Phase 2 fixdep make route\n'
                '        run: make -C zigux phase2-fixdep\n',
            ),
            encoding='utf-8',
        ),
        'workflow make-route packet must finish before the required-make-routes self-test',
    )
    expect_fail(
        lambda root: (root / MAKEFILE_REL).write_text(
            read_text(root / MAKEFILE_REL).replace(
                '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py\n',
                '',
            ),
            encoding='utf-8',
        ),
        'Makefile recipe line $(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py must appear exactly once',
    )
    expect_fail(
        lambda root: (root / MAKEFILE_REL).write_text(
            read_text(root / MAKEFILE_REL).replace(
                '.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3-validate phase3\n',
                '.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-fixdep phase2-validate phase2 phase3-validate phase3\n',
            ),
            encoding='utf-8',
        ),
        'Makefile .PHONY targets must include the current Phase 2 route set',
    )
    expect_fail(
        lambda root: (root / WORKFLOW_REL).write_text(
            read_text(root / WORKFLOW_REL).replace(
                'Run current Phase 2 fixdep make route',
                'Run current Phase 2 toolchain make route',
                1,
            ),
            encoding='utf-8',
        ),
        'workflow step Run current Phase 2 toolchain make route must appear exactly once',
    )

    print('PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET_SELF_TEST=pass')
    print(f'PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET_SELF_TEST_CASE_COUNT={case_count}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate the current Lane 03 bootstrap make-route packet.')
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Repository root to validate.')
    parser.add_argument('--write-sample-root', type=Path, help='Write a minimal passing sample root and exit.')
    parser.add_argument('--self-test', action='store_true', help='Run built-in self-tests.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f'PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET_SAMPLE_ROOT={args.write_sample_root}')
        return 0

    try:
        validate_root(args.root)
    except ValidationError as exc:
        print('PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET=fail')
        print(f'PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET_ROOT={args.root}')
        print(f'PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET_NOTE={exc}')
        return 1

    print('PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET=pass')
    print(f'PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET_ROOT={args.root}')
    print(f'PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET_WORKFLOW_STEP_COUNT={len(WORKFLOW_STEPS)}')
    print(f'PHASE2_BOOTSTRAP_MAKE_ROUTE_PACKET_MAKE_TARGET_COUNT={len(MAKEFILE_TARGET_LINES)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
