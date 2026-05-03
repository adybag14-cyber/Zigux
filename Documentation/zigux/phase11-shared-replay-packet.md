# Phase 11 Shared Replay Packet

This note records the shared Phase 11 replay packet that current `master` already keeps live through `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `scripts/zigux/check-phase11-build-inventory.py`.

## Shared replay surface

The shared Phase 11 replay remains the validator-backed `zig build test --build-file zigux/tests/phase11_build.zig --summary all` path.

That shared packet now includes the bounded split or follow-up replays that sit beside the starter tests instead of hiding only in local file history:

- `zigux/tests/phase11_dw_wdt_suspend_resume.zig`
- `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`

## Pinned replay markers

The committed build-inventory fixture currently pins one exact review marker from each shared replay surface:

- `zigux/tests/phase11_dw_wdt_suspend_resume.zig`: `summary.resume_preserves_timeout_programming`
- `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`: `reset_available_summary.remove_clears_interrupt_status`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`: `summary.tiocmset_result` with the focused `-7` callback result
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`: `dispatch.invokes_sysrq_handler`

Those markers keep the current shared replay packet reviewable without claiming that the broader driver families are already closed.

## Dedicated boundary

`zigux/tests/phase11_hvc_console_survey.zig` still stays outside the shared `test_step` and remains the dedicated archival replay behind `make -C zigux phase11-hvc-survey`.

That split keeps the current hvc survey packet explicit without silently implying that every Phase 11 survey gate already runs inside the shared starter path.

## Review path

The published review path for this packet is:

- `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase11-build-inventory.py`
- `python3 scripts/zigux/validate-phase11.py --self-test`
- `make -C zigux phase11-validate`
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11-hvc-survey`

## Non-goals

This packet does not claim new live platform registration, watchdog-core registration, notifier execution, khvcd execution, or host-backed teardown behavior.

The next bounded simple-driver follow-up should stay inside validator, fixture, or review-packet maintenance unless fresh repo inspection exposes another comparably small driver-local gap.
