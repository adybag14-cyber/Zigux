# Phase 13 devres Non-Posted Wrapper Gap

This bounded `P13-L06` note records one remaining reminder-surface exactness gap inside the active Phase 13 `lib/devres.c` helper packet on current `master`.

## Roadmap Fit

Phase 13 in the roadmap keeps `lib/devres.c` inside the shared-subsystem-helper tranche. That makes reminder truthfulness part of the shipped product surface, not just helper-local cleanup.

## What Current `master` Already Makes Explicit

The helper-local iomap/MMIO packet already names the blocked non-posted wrapper directly:

- `Documentation/zigux/phase13-devres-iomap-planner.md` says the translated helper-first remap would still require the blocked `devm_ioremap_np()` wrapper
- `Documentation/zigux/phase13-devres-survey.md` keeps blocked `phase13-devres-missing-devm-ioremap-np-surface` explicit inside the current devres MMIO packet
- `zigux/tests/phase13_devres_iomap_planner_manifest.json` records that same blocked boundary in the packet manifest
- `zigux/tests/phase13_devres_iomap_planner.zig` keeps the blocked non-posted wrapper requirement reviewable in direct replay coverage
- `scripts/zigux/check-phase13-devres-iomap-planner.py` fail-closes on the packet-local `devm_ioremap_np()` boundary wording
- `lib/devres.zig` keeps `requires_nonposted_ioremap` helper-local while still leaving live `devm_ioremap_np(` absent from shipped helper code

## Gap

The broader shared reminder stack now mirrors the widened devres packet, but it still does not carry the blocked non-posted MMIO wrapper by name through:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`

That means the packet-local evidence is truthful while the broader contributor and release summaries still rely on the reader to infer the specific non-posted MMIO blocker from the narrower devres note set.

## Why This Matters

This lane is about iomap/MMIO safety surface exactness, not new helper behavior. Keeping the blocked `devm_ioremap_np()` wrapper explicit where shared reminder wording is already enumerating the widened devres packet reduces the chance that the lane looks more complete than current `master` actually is.

## Guard

Use `python3 scripts/zigux/check-phase13-devres-np-wrapper-gap.py` when touching this note or the surrounding shared Phase 13 reminder stack.

That checker should pass only while:

- the helper-local devres iomap packet still names the blocked `devm_ioremap_np()` surface directly
- the three broader shared reminder notes above still omit that explicit blocker

## Next Bounded Step

If a future same-lane reminder refresh needs to carry the non-posted MMIO blocker into one of the broader shared Phase 13 summaries, update that shared reminder surface and retire this gap note in the same change instead of widening helper behavior.