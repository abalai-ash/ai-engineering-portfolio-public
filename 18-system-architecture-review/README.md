# System Architecture Review

A synthetic environmental-monitoring workflow is decomposed into functions,
logical components, physical resources, interfaces, and allocations.

The review checks whether functions are assigned, interfaces connect valid
components, required data fields are defined, dependencies remain consistent,
and architecture alternatives satisfy the stated constraints.

## Included work

- operational context and external actors
- functional decomposition
- logical component architecture
- physical resource allocation
- interface definitions
- function-to-component allocation
- dependency and connection checks
- architecture review findings
- design alternative comparison
- JSON, CSV, and Markdown reports
- automated tests

## Scope

The project uses synthetic monitoring requests, sensor configurations,
measurement records, validation products, resource allocations, interfaces,
and design alternatives to demonstrate architecture-review methods.

## Environmental and subsurface transfer

The architecture separates monitoring requests, planning, sensor
configuration, measurement collection, validation, and evidence transfer into
distinct functions and components.

The same structure can support synthetic subsurface workflows by replacing the
measurement type and domain-specific validation rules while retaining the
allocation, interface, dependency, resource, and trade-study checks.

## Run

    python3 eval/evaluate.py
    python3 -m unittest discover -s tests -v

Generated reports are written locally to reports/.

## Goals

- Connect monitoring functions to components, resources, and interfaces.
- Identify incomplete allocations and inconsistent architecture records.
- Compare architecture alternatives using explicit review criteria.

## Lessons

- Architecture reviews are clearer when functions and interfaces are modeled
  separately from implementation details.
- Allocation and dependency checks expose integration issues early.
- Explicit interface fields make data handoffs easier to review.

## Accomplishments

- Structured a synthetic environmental-monitoring workflow across functional,
  logical, and physical views.
- Added automated checks for allocations, interfaces, dependencies, resource
  capacity, and design alternatives.
- Preserved deterministic reports and a repeatable trade-study result.
