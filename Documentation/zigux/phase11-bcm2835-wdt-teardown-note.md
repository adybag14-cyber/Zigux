# Phase 11 BCM2835 Watchdog Teardown Note

This note records the bounded teardown and restart or poweroff surface that is directly reviewable in the current Zigux `bcm2835_wdt` starter packet.
It stays inside the bcm2835 watchdog lane and avoids describing larger registration or remove flows that the current direct read path still cannot materialize end to end, while keeping the shared-contract raw replay and verify route explicit.

## Status

- `PHASE11_BCM2835_WDT_TEARDOWN_STATUS=driver_teardown_truthful`
- archival packet identity remains `P11-L08`
- lane scope: keep the current bcm2835 watchdog stop, restart, and poweroff story reviewable without widening into platform registration, PM-base plumbing, shared callback installation, or hardware-backed execution
- directly readable bcm2835 reminder packet for this note:
  - `drivers/watchdog/bcm2835_wdt.zig`
  - `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- shared-contract raw-fallback bcm2835 replay route kept in view for this note:
  - `zigux/tests/phase11_bcm2835_wdt.zig`
  - `drivers/watchdog/bcm2835_wdt_verify.zig`
  - `zigux/tests/phase11_build.zig`

## Teardown And Poweroff Surface

The current directly readable bcm2835 driver starter keeps one small teardown boundary explicit:

- `summarizeProbe()` keeps the system-power-controller split and the claimed-versus-conflicting poweroff-handler summary readable before any live callback installation is implied.
- `Bcm2835WdtLab.stop()` owns the bounded stop path by recording `reset_register_written`, `running_before_stop`, `running_after_stop`, and `full_reset_armed_after_stop`.
- `Bcm2835WdtLab.restart()` owns the short restart-arm path by recording the fixed restart timeout ticks, the full-reset posture, the bounded delay marker, and the running state after restart intent.
- `Bcm2835WdtLab.poweroff()` keeps the halt-partition request and restart-path reuse explicit without claiming that a shared platform poweroff callback was actually installed or executed.
- `Bcm2835WdtLab.importBootloaderRunning()` keeps the imported running-state checkpoint readable so the restart and poweroff path can be reviewed from a nonzero time-left starting point.

| boundary | current Zigux owner | what stays reviewable now | still out of scope |
| --- | --- | --- | --- |
| probe-time ownership summary | `summarizeProbe()` | system-power-controller split, claimed-versus-conflicting handler summary, and bounded registration intent flags | live callback installation, platform probe execution, and watchdog-core registration |
| stop path | `Bcm2835WdtLab.stop()` | reset-register-written intent, running-state transition, and full-reset clear posture | real register IO, driver remove ordering, and hardware-backed shutdown |
| restart path | `Bcm2835WdtLab.restart()` | restart timeout ticks, full-reset request posture, delay marker, and running-after-restart intent | reboot notifier wiring, platform restart execution, and board timing |
| poweroff path | `Bcm2835WdtLab.poweroff()` | halt-partition request, restart-path reuse, short restart arm posture, and running-after-poweroff summary | shared callback installation, PM-base plumbing, and board-backed poweroff execution |
| imported running checkpoint | `Bcm2835WdtLab.importBootloaderRunning()` | bootloader-running carry-in state before restart or poweroff review | live boot firmware handoff and probe-time MMIO observation |
| replay and verify route presence | the shared Phase 11 contract plus the named replay and verify paths | reviewable evidence that the teardown reminder sits beside a bcm2835 replay file, verify route, and shared Phase 11 build path even though the whole archival packet is not directly readable end to end | manifest-backed survey closure, directly readable remove-path closure, and broader platform-backed teardown validation |

## Review Rules

- Treat this note as a bounded ownership and teardown reminder for the current directly readable driver starter, not as proof of live platform remove or shared callback execution.
- Keep this note aligned with `drivers/watchdog/bcm2835_wdt.zig`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, and `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` when the directly readable stop, restart, or poweroff helpers change.
- Do not describe manifest-backed packet closure or survey-gated teardown coverage as live current-master evidence until those paths are directly readable again in this lane, but keep the shared-contract raw replay and verify route named truthfully when this reminder packet refers to adjacent bcm2835 evidence.
- If a later Phase 11 lane widens the bcm2835 packet into dedicated manifest or survey closure work, refresh this note together with the bcm2835 survey and matrix so the teardown story stays truthful.

## Next Blocked Step

The next honest bcm2835 follow-through remains one manifest-backed, survey-gated, or checker-backed extension that matches the current driver starter plus the already recorded replay route. Until then, keep this teardown note bounded to the driver-local stop, restart, and poweroff model already visible on `master`.
