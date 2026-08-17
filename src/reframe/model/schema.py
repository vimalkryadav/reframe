"""Structured-output schema for what the model reads off a montage.

Every field is **required**. A structured-output schema with optional fields lets
the model omit what it could not determine, and an omitted field is
indistinguishable from a field nobody asked about. Requiring all of them forces
an explicit ``null`` — and ``null`` plus a stated reason in ``unreadable`` is a
usable record, where silence is not.

The shape is also deliberately narrow. There is no colour field and no place to
put a data-grid value, because a schema that offers a slot invites the model to
fill it (DEC-011).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ScreenReading(BaseModel):
    """One labelled strip, as read."""

    model_config = ConfigDict(extra="forbid")

    frame_id: str = Field(
        description="The frame id burnt into this strip's label, copied exactly.",
    )
    name: str | None = Field(
        description=(
            "The screen or activity name as printed in the title band. Null if the "
            "text cannot be read with confidence — never a guess and never inferred "
            "from the surrounding screens."
        )
    )
    module: str | None = Field(
        description=(
            "The application area or module this screen belongs to, only if it is "
            "printed on screen. Null otherwise."
        )
    )
    tabs: list[str] = Field(
        description=(
            "Tab or sub-tab labels visible in the strip, left to right, exactly as "
            "printed. Empty list if none are visible."
        )
    )
    dialog: str | None = Field(
        description=(
            "The title of a dialog, modal or overlay covering the screen, if one is "
            "open. Null if no dialog is visible."
        )
    )
    structure: str | None = Field(
        description=(
            "One short sentence on the layout — regions, control types, how the "
            "screen is arranged. Never colours. Never values from any data row."
        )
    )
    unreadable: str | None = Field(
        description=(
            "Why this strip could not be read: blur, glare, the band being cut off, "
            "or text too small. Null when the strip was read cleanly. Required "
            "whenever name is null."
        )
    )


class MontageReading(BaseModel):
    """One entry per strip on the sheet, in the order they appear."""

    model_config = ConfigDict(extra="forbid")

    screens: list[ScreenReading] = Field(
        description="One entry per labelled strip, top to bottom. Do not merge or skip strips."
    )


class FrameReading(BaseModel):
    """A single full frame, for screens the montage pass could not resolve."""

    model_config = ConfigDict(extra="forbid")

    screen: ScreenReading
