Stability policy
================

PREP-SHOT's stability surface evolves across major versions. Each major
version makes a different promise about what is allowed to break.

v1.x — research / evolving (current)
------------------------------------

Use v1.x for active research; pin to a specific tag (e.g. ``v1.1.0``) for
any reproducible study.

* The Python entry point ``prepshot.create_model(params)`` is **stable**;
  arguments and return type will not change in v1.x.
* The ``params.json`` input schema is **evolving** and tracked by
  ``_schema_version`` (currently ``1``). Breaking changes can land on
  minor version bumps within v1.x. See :doc:`Changelog` for each bump.
* The ``prepshot/_model/`` sub-package internals (constraint classes, rule
  methods) are **internal**; they may change without notice.

v2.0 — stable (planned)
-----------------------

When the input schema and Python API both feel right:

* Both surfaces will be promised stable.
* Breaking changes will require a major version bump.
* A migration registry (``prepshot/migrations/``) will be in place so that
  future schema bumps come with automated migrations.
