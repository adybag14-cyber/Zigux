# Zigux Review Checklist

Use this checklist before opening or merging Zigux product work.

## Scope
- is the target phase named explicitly?
- is the status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?
- is the Linux anchor file or tree path named directly?

## Safety
- does the change avoid mirror-tree sprawl?
- is real code co-located with the owning Linux subsystem when appropriate?
- does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?

## Validation
- are parity tests or fixture checks included?
- is there a stated performance gate if the code is algorithmic, queueing-sensitive, or driver-facing?
- is there a stated rollback owner and fallback path?

## ABI and Runtime
- are bindings and ABI assumptions centralized?
- does the change avoid hidden runtime services, implicit allocation, or unclear panic behavior?
- if unsafe code exists, is it narrow, visible, and review-owned?

## Product Discipline
- does the patch make Zigux more buildable, more testable, or more reviewable?
- if it came from ZAR research, is the transfer rationale explicit?
- does the change strengthen the product repo instead of just extending experimental scope?
