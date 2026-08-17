"""Reframe — handheld recordings of a desktop application into a screen catalogue.

The package is split three ways and the split is load-bearing:

``stages/``   orchestrate — read the manifest, call compute, write the manifest
``vision/``   compute — pure image functions, no pipeline awareness
``model/``    compute — prompts, client, schema

Nothing in ``stages/`` holds an algorithm and nothing in ``vision/``/``model/``
holds pipeline logic. See ``CLAUDE.md``.
"""

__version__ = "0.1.0"

# Bumped when the manifest's shape changes in a way older output cannot satisfy.
MANIFEST_SCHEMA_VERSION = 1
