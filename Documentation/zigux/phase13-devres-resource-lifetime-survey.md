# Phase 13 Devres Resource Lifetime Survey

Lane: `P13-L07`
Phase: `Phase 13`
Roadmap anchor set: `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, `security/landlock/syscalls.c`
Surveyed commit: `e7a3a1b2a55972961337186320d2ee31e64496db` (`Align Phase 13 notifier priority checker with repo reality`)

## Repo Reality

The roadmap explicitly calls for resource lifetime helpers under `lib/devres.zig`, but the current repo state still centers the usable evidence in `lib/devres.c`. The visible `lib/devres.zig` peer is still an empty placeholder rather than a reviewed helper slice.

The C anchor already exposes a bounded lifetime-helper surface worth porting carefully:

- `devm_ioremap`
- `devm_ioremap_resource`
- `devm_ioport_map`
- `devm_arch_phys_wc_add`
- `devm_arch_io_reserve_memtype_wc`

Those exports show that Phase 13 does not need a speculative shared-helper subtree to move forward. The real gap is a reviewed leaf helper that preserves managed allocation, release, and error-return behavior.

## Churn Warning

The latest visible Phase 13 commit during this run was `e7a3a1b2a55972961337186320d2ee31e64496db`, titled `Align Phase 13 notifier priority checker with repo reality`. That is useful maintenance work, but it also confirms that current lane-family activity is not yet delivering `devres` parity itself.

Because the repo already shows a large amount of helper-shaped growth elsewhere, broadening this lane into more shared-subsystem helper wrappers would risk shared-subsystem helper churn instead of real Phase 13 parity progress.

## Next bounded step

Next bounded step:

Start with a managed ioremap/resource wrapper slice inside `lib/devres.zig`:

1. model the `devm_ioremap` allocation-and-release path
2. add the `devm_ioremap_resource` request-region/error-return wrapper on top
3. keep the survey packet until that slice has focused parity notes and a narrow Zig validation pass
