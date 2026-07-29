# Design notes

The requirement structure separates stakeholder needs, system requirements,
and subsystem requirements.

Each requirement records:

- its parent
- allocated component
- verification method
- approval state

Verification cases may cover more than one requirement when the same evidence
supports related system and subsystem behavior.

Baseline comparison is limited to stable requirement fields so that wording or
approval changes can be reviewed without treating generated report content as
part of the baseline.

Change-impact analysis follows child requirement links and then gathers the
verification cases and components associated with the affected requirements.

The example is synthetic and does not reproduce a real instrument, facility,
research program, or proprietary workflow.
