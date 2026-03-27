# ZAR to Zigux Product Roadmap

## Purpose

This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.

Positioning:
- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.
- `Zigux` is the product repo.
- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.

This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.

## Inputs Reviewed

The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:
- `zigux_bundle_review_v2.csv`
- `zigux_full_parity_focus_v2.csv`
- `zigux_linux_to_zigux_map_v2.csv`
- `zigux_master_phases_v2.csv`
- `zigux_phase_targets_v2.csv`
- `zigux_pm_roadmap_v2.xlsx`
- `zigux_risk_register_v2.csv`
- `zigux_sources_v2.csv`
- `zigux_structure_v2.csv`
- `zigux_workstreams_v2.csv`

I also checked the current public repo state at:
- <https://github.com/adybag14-cyber/Zigux>

## Bundle Normalization Notes

The workbook and CSV corpus are directionally aligned, but the workbook executive summary contains stale aggregate counts.

Normalized counts from the extracted structured files:
- phases: `15`
- phase targets: `60`
- parity-focus rows: `12`
- workstreams: `15`
- risks: `12`
- structure rules: `18`
- source anchors: `61`

Stale executive-summary metadata in the workbook that should not drive planning:
- phases: `17`
- file-level target rows: `62`
- workstreams: `17`
- risks: `14`

For execution, use the structured CSV/workbook tables themselves, not the executive-summary metrics block.

## Non-Negotiable Product Rules

These rules are consistent across the bundle and should govern every Zigux commit series.

1. No flag-day rewrite.
- Zigux grows through mixed-language coexistence.
- C remains in place until each bounded area proves parity and maintainability.

2. No mirror-tree sprawl.
- Do not build a fake parallel kernel under a generic Zigux namespace.
- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.

3. Co-locate product code with Linux ownership.
- Host-side helper ports belong beside current files such as `tools/lib/*.zig`.
- Runtime helper ports belong beside current files such as `lib/*.zig`.
- Driver pilots belong in current subsystem trees such as `drivers/virtio/*.zig`.

4. Keep the Zigux support root small.
- The support root exists for boundary code, not for duplicating Linux subsystems.
- The intended long-term support root is:
  - `zigux/kernel/`
  - `zigux/helpers/`
  - `zigux/bindings/`
  - `zigux/uapi/`
  - `zigux/tests/`
  - `zigux/unsafe/`

5. Port leaf helpers before shared runtime helpers.
- Port shared runtime helpers before drivers.
- Port simple drivers before high-throughput queueing and DMA-heavy drivers.

6. Validation is mandatory before expansion.
- Every approved target needs parity tests.
- Every sensitive path needs a perf threshold.
- Every migration needs a rollback owner.

7. Wrapper-first or dual-implementation is the default where semantics are risky.
- Build tooling
- ABI/export surfaces
- allocators
- atomics and barriers
- MMIO
- virtio rings
- DMA-sensitive drivers
- tracing and queueing infrastructure

8. Deep-core freeze is real.
- Do not move these into active delivery before the roadmap says so:
  - `kernel/sched/core.c`
  - `mm/page_alloc.c`
  - `kernel/rcu/tree.c`
  - `net/core/skbuff.c`
- Treat `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` as boundary-study targets first, not rewrite targets.

9. Human review remains mandatory.
- Follow Linux process expectations.
- Use AI-assisted work only as a human-reviewed aid, not as an autonomous authority.

## How ZAR Should Feed Zigux

ZAR should not try to become Zigux.

ZAR should instead feed Zigux in these ways:

| ZAR capability or work type | Use for Zigux | How to transfer it | Zigux phase impact |
| --- | --- | --- | --- |
| parity gates and drift checks | High | Rebuild as Linux-facing differential gates inside `zigux/tests/` and `scripts/zigux/` | 2-4 |
| build reproducibility discipline | High | Transfer the release-gate mindset, not the exact scripts | 2-4 |
| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |
| bare-metal i386 platform and SMP research | Medium | Use as concurrency-validation research input only | 4, 9, 14 |
| virtio, E1000, RTL8139 proof methodology | Medium | Reuse the validation mindset and probe culture, not the current ZAR code shape | 9-12 |
| storage and filesystem probe methodology | Medium | Reuse for `fs/libfs`, `lib/devres`, and driver validation scaffolding | 4, 13 |
| shell, TTY, tool-service runtime | Low | Product value is indirect; use only where it informs repo-hosted tooling or validation UX | 4-8 |
| workspace/package/trust runtime | Low | Mostly ZAR-specific; keep out of near-term Zigux product scope | research only |
| VFS overlay experiments | Medium | Use only as design lessons for bounded helper layers, not as a direct port target | 13-15 |
| driver lifecycle proofs | High | Use to shape lab matrices, teardown checks, and failure-mode expectations | 10-12 |

The rule is simple:
- If a ZAR slice reduces Zigux product risk, keep it.
- If it only expands ZAR’s own experimental surface, do not let it consume Zigux product bandwidth.

## zigux-alpha Scope

`zigux-alpha/` is the staging area for:
- roadmap and phase sequencing
- source mapping
- validation strategy
- freeze map
- first commit ledger
- workstream ownership

`zigux-alpha/` is not the final home for:
- subsystem ports
- runtime helpers
- drivers
- bindings
- UAPI shims

Those should eventually land in:
- `tools/lib/*.zig`
- `scripts/zigux/`
- `zigux/`
- `Documentation/zigux/`
- `samples/zigux/`
- `lib/*.zig`
- `drivers/*/*.zig`
- `fs/*.zig`
- `security/*/*.zig`

## Product Features by Phase

## Phase 1: Alpha Host-Side Helpers

Primary product goal:
- prove that Zig can live in-tree on low-risk host-side helper code

Primary Linux targets:
- `tools/lib/bitmap.c`
- `tools/lib/find_bit.c`
- `tools/lib/string.c`
- `tools/lib/rbtree.c`

Required Zigux features:
- mixed-language helper build path
- golden-output parity tests
- clear ownership and review rules for `.zig` files beside `.c`

Recommended Zigux destinations:
- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/string.zig`
- `tools/lib/rbtree.zig`

Why ZAR matters here:
- ZAR already shows disciplined phase tracking, probe-driven validation, and explicit boundaries. That process discipline should be ported immediately.

## Phase 2: Toolchain and Kbuild Enablement

Primary product goal:
- make Zigux buildable, reproducible, and acceptable inside Linux-style workflows

Primary Linux targets:
- `scripts/basic/fixdep.c`
- `scripts/genksyms/genksyms.c`
- `scripts/kconfig/conf.c`
- `scripts/kconfig/confdata.c`

Required Zigux features:
- compiler pinning and upgrade policy
- deterministic artifact checks
- selected dual implementations
- wrapper-first path for parser-heavy tooling
- cross-arch build matrix

Recommended Zigux destinations:
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/Makefile`

Why ZAR matters here:
- ZAR’s insistence on freshness checks, pinned validation, parity gates, and CI-after-push discipline should become default Zigux behavior.

## Phase 3: ABI and Interop Substrate

Primary product goal:
- define the permanent C/Zigux boundary

Primary Linux anchors:
- `rust/exports.c`
- `lib/bitmap.c`
- `lib/rbtree.c`
- `lib/cpumask.c`

Required Zigux features:
- explicit export shims
- generated or curated bindings
- layout assertions
- explicit panic policy
- explicit allocator policy
- approved atomic, barrier, and MMIO wrappers
- narrow unsafe surface

Recommended Zigux destinations:
- `zigux/kernel/`
- `zigux/helpers/`
- `zigux/bindings/`
- `zigux/uapi/`
- `zigux/unsafe/`
- `include/linux/zigux.h`
- `include/zigux/abi.h`

Why ZAR matters here:
- ZAR’s exported runtime state, ABI gating, and explicit failure-code discipline are directly useful as a product engineering habit, even though the actual Zigux substrate must be Linux-kernel-specific.

## Phase 4: Differential Validation and Rollback

Primary product goal:
- make every future Zigux port measurable and reversible

Primary Linux anchors:
- `lib/atomic64_test.c`
- `lib/test_bitmap.c`
- `samples/kprobes/kprobe_example.c`
- `samples/vfs/test-fsmount.c`

Required Zigux features:
- `zigux/tests/` parity harnesses
- perf baselines and thresholds
- rollback ownership
- lab and CI matrices
- artifact-diff checks for host-side tools

Recommended Zigux destinations:
- `zigux/tests/atomic64_diff.zig`
- `zigux/tests/bitmap_diff.zig`
- `samples/zigux/kprobe_example.zig`
- `samples/zigux/test_fsmount.zig`
- `scripts/zigux/` diff and layout tools

Why ZAR matters here:
- This is the strongest area to port from ZAR’s current practice. ZAR already behaves like a validation-first system; Zigux should inherit that immediately.

## Phase 5: Samples and Reference Patterns

Primary product goal:
- make approved Zigux idioms reviewable and repeatable

Primary Linux anchors:
- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Required Zigux features:
- side-by-side sample ports
- ownership and lifetime examples
- tracing examples
- review checklist and contributor guide

Recommended Zigux destinations:
- `samples/zigux/`
- `Documentation/zigux/`

## Phase 6: Greenfield Leaf Helpers

Primary product goal:
- allow low-risk new helper code in Zigux without taking runtime-core risk

Primary Linux anchors:
- `lib/base64.c`
- `lib/bsearch.c`
- `lib/checksum.c`
- `lib/hexdump.c`

Required Zigux features:
- leaf helper portability
- clear API parity
- perf gates for math-sensitive helpers

Recommended Zigux destinations:
- `lib/base64.zig`
- `lib/bsearch.zig`
- `lib/checksum.zig`
- `lib/hexdump.zig`

## Phase 7: In-Kernel Leaf Libraries

Primary product goal:
- bring the first reusable runtime helper families into the product path

Primary Linux anchors:
- `lib/string_helpers.c`
- `lib/cmdline.c`
- `lib/argv_split.c`
- `lib/rbtree.c`

Required Zigux features:
- runtime-safe leaf helpers
- stronger ownership and pointer discipline
- integration with validation substrate

Recommended Zigux destinations:
- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

## Phase 8: Userspace-Adjacent Tooling Expansion

Primary product goal:
- prove Zigux inside serious repo-hosted tooling, not just tiny helpers

Primary Linux anchors:
- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/help.c`
- `tools/lib/symbol/kallsyms.c`
- `tools/lib/bpf/libbpf.c`

Required Zigux features:
- helper-first expansion
- segmented plan for large consumers like libbpf
- output-stable tooling behavior

Recommended Zigux destinations:
- `tools/lib/subcmd/*.zig`
- `tools/lib/symbol/*.zig`
- `tools/lib/bpf/zigux_segments/`

## Phase 9: Runtime Pilot Modules

Primary product goal:
- enter runtime kernels through tests and samples, not production pressure

Primary Linux anchors:
- `lib/atomic64_test.c`
- `lib/test_bitmap.c`
- `samples/trace_events/trace-events-sample.c`
- `samples/kprobes/kretprobe_example.c`

Required Zigux features:
- first loadable Zigux runtime modules
- selftest hooks
- runtime module lifecycle parity

Recommended Zigux destinations:
- `zigux/tests/runtime_*`
- `samples/zigux/runtime_*`

## Phase 10: Virtio and Lab Drivers

Primary product goal:
- prove the driver model on VM-friendly transports before touching harder hardware

Primary Linux anchors:
- `drivers/virtio/virtio.c`
- `drivers/virtio/virtio_ring.c`
- `drivers/virtio/virtio_mmio.c`
- `drivers/virtio/virtio_input.c`

Required Zigux features:
- virtqueue wrappers
- MMIO wrappers
- lab-only driver validation
- dual implementations for risky areas

Recommended Zigux destinations:
- `drivers/virtio/*.zig`
- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified

Why ZAR matters here:
- ZAR’s virtio driver and probe experience is relevant as lab methodology and validation design, not as direct Linux product code.

## Phase 11: Simple Production Drivers

Primary product goal:
- move from lab drivers to bounded real hardware drivers with straightforward lifecycles

Primary Linux anchors:
- `drivers/watchdog/gpio_wdt.c`
- `drivers/watchdog/bcm2835_wdt.c`
- `drivers/watchdog/dw_wdt.c`
- `drivers/tty/hvc/hvc_console.c`

Required Zigux features:
- direct-port or dual-impl driver templates
- hardware validation matrix
- teardown and failure-mode parity

Recommended Zigux destinations:
- `drivers/watchdog/*.zig`
- `drivers/tty/hvc/*.zig`

## Phase 12: Complex Production Drivers and Heavy Helper Consumers

Primary product goal:
- take on high-value, high-risk drivers only after earlier proof

Primary Linux anchors:
- `drivers/net/virtio_net.c`
- `drivers/nvme/host/pci.c`
- `drivers/scsi/virtio_scsi.c`
- `tools/lib/bpf/libbpf.c`

Required Zigux features:
- DMA-safe abstractions
- queueing correctness
- throughput and recovery parity
- segmented rollout

Recommended Zigux destinations:
- `drivers/net/virtio_net.zig`
- `drivers/nvme/host/pci.zig`
- `drivers/scsi/virtio_scsi.zig`
- `tools/lib/bpf/zigux_segments/`

## Phase 13: Shared Subsystem Helpers

Primary product goal:
- port bounded helper layers shared across multiple runtime consumers

Primary Linux anchors:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Required Zigux features:
- filesystem helper wrappers
- resource lifetime helpers
- bounded security helper pilots

Recommended Zigux destinations:
- `fs/libfs.zig`
- `lib/devres.zig`
- `security/landlock/*.zig`

## Phase 14: Core-Adjacent Bounded Internals

Primary product goal:
- study or wrap critical shared infrastructure without claiming premature parity

Primary Linux anchors:
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- `net/core/skbuff.c`
- `kernel/rcu/tree.c`

Required Zigux features:
- boundary maps
- concurrency audits
- explicit stay-in-C decisions where warranted
- wrapper-first or study-only posture

Recommended Zigux destinations:
- `kernel/workqueue_bridge.zig`
- `kernel/trace/ring_buffer.zig` only if years of evidence justify it
- `net/core/skbuff_bridge.zig`
- `kernel/rcu/tree_bridge.zig`

## Phase 15: Full-Parity Blockers and Long-Term Governance

Primary product goal:
- govern the final mixed-language steady state honestly

Primary Linux anchors:
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

Required Zigux features:
- freeze map
- Architecture Council review process
- parity scorecard
- policy for code that remains in C indefinitely

This phase is about discipline, not bravado.

## Freeze Map for Near- and Mid-Term Planning

Active freeze-in-C targets for the current product plan:
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

Boundary-study-only targets before any direct port decision:
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

What this means for ZAR future work:
- research on these areas can continue in ZAR if it improves understanding
- those experiments should not be represented as near-term Zigux delivery commitments

## Workstreams and Ownership Model

The bundle supports a 15-workstream execution model.

Core workstreams:
- Architecture Council
- PMO / Release Management
- Host Tools Alpha Pod
- Toolchain and Kbuild Team
- ABI and Runtime Team
- Validation and Perf Team
- Developer Enablement
- Kernel Leaf Libraries Pod
- Repo Tooling Pod
- Runtime Pilot Pod
- Virtio Driver Pod
- Simple Drivers Pod
- Complex Drivers and Infra Pod
- Shared Subsystems Pod
- Core-Adjacent Pod

For Zigux, that means every active commit series should declare:
- owner
- phase
- status bucket
- validation gate
- rollback owner

## Risk Register That Must Drive Prioritization

The highest-risk items from the bundle are the ones that must shape scope:
- mirror-tree sprawl
- toolchain instability
- ABI and layout drift
- hidden runtime behavior
- memory-ordering mistakes
- insufficient validation before expansion
- reviewability collapse
- DMA and queueing regressions
- resource-lifetime mis-modeling
- overpromising full parity
- upstream process misalignment
- deep-core scope creep

The most important operational consequence is this:
- if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership, it is not ready for the product repo

## First Commit and Push Sequence for Zigux

This is the recommended near-term commit train after this roadmap lands.

### Bootstrap commits

1. `docs(zigux-alpha): establish roadmap and folder charter`
- add `zigux-alpha/README.md`
- add this roadmap

2. `docs(Documentation/zigux): add program charter and freeze map`
- create `Documentation/zigux/README.md`
- create `Documentation/zigux/review-checklist.md`
- create `Documentation/zigux/freeze-map.md`

3. `build(scripts/zigux): add toolchain pinning and version checks`
- create `scripts/zigux/`
- add Zig toolchain version policy
- add deterministic version-check helper

4. `test(zigux/tests): add differential harness scaffolding`
- create `zigux/tests/`
- add bitmap and atomic parity harness scaffolds
- add artifact-diff scaffolds for host-side tools

### Phase 1 commits

5. `feat(tools/lib): add bitmap.zig host helper port`
6. `feat(tools/lib): add find_bit.zig host helper port`
7. `feat(tools/lib): add string.zig host helper port`
8. `feat(tools/lib): add rbtree.zig host helper port`
9. `test(tools/lib): add golden-output parity gates for alpha helper ports`

### Phase 2 commits

10. `feat(scripts/zigux): add fixdep dual implementation`
11. `feat(scripts/zigux): add genksyms dual implementation`
12. `feat(scripts/zigux): add kconfig bridge scaffolding`
13. `ci(zigux): add cross-arch build and artifact diff matrix`

### Phase 3 and 4 commits

14. `feat(zigux): add ABI, bindings, and export substrate skeleton`
15. `test(zigux/tests): add atomic64 and runtime bitmap differential gates`
16. `docs(Documentation/zigux): add unsafe policy and interop rules`

### Phase 5 commits

17. `feat(samples/zigux): add reference samples for fifo, kobject, kretprobe, and trace events`
18. `docs(Documentation/zigux): add sample-backed review guide`

Do not schedule Phase 10+ commits until the earlier gates are actually green.

## Recommended Validation Gates

Every approved Zigux slice should declare and satisfy these gates.

1. Build gate
- deterministic artifact generation where applicable
- pinned toolchain version
- reproducible host-side outputs

2. ABI gate
- layout assertions
- calling-convention checks
- one blessed export surface

3. Behavior gate
- differential tests against current C behavior
- fixture or known-vector parity

4. Performance gate
- perf thresholds for algorithmic helpers and driver-sensitive paths

5. Runtime gate
- load/unload behavior for runtime modules
- teardown parity
- queueing and failure-path coverage for drivers

6. Rollback gate
- named owner
- explicit fallback to current C implementation
- clear disable path when regressions appear

## What Should Start Next in Zigux

Immediate next steps after this document lands:

1. keep `zigux-alpha/` as the control-plane for startup planning only
2. create `Documentation/zigux/` and `scripts/zigux/`
3. create `zigux/tests/` differential harness scaffolding
4. deliver Phase 1 host-side helper ports in `tools/lib/*.zig`
5. do not start runtime kernel ports before the Phase 2-4 gates are in place

## Final Direction

Zigux succeeds if it behaves like a disciplined Linux product program, not like a language rewrite experiment.

That means:
- small support root
- co-located subsystem ports
- strong validation
- explicit freeze map
- commit trains that move from bounded helper wins to toolchain maturity to substrate maturity to runtime pilots

ZAR future work should now be judged against one question:
- does this make a future Zigux commit smaller, safer, or more testable?

If yes, keep investing.
If no, keep it in research and do not let it drive the product roadmap.
