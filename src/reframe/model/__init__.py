"""Prompts, client and schema for the one stage allowed to call a model.

No pipeline logic lives here: this package renders a request, validates a
response, and caches the pair. What to do with a screen that could not be read is
stage 06's decision.
"""
