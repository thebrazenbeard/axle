from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MotionState(str, Enum):
    PARKED = "parked"
    MOVING = "moving"
    UNKNOWN = "unknown"

    @classmethod
    def parse(cls, value: str) -> "MotionState":
        try:
            return cls(value.strip().lower())
        except (ValueError, AttributeError):
            return cls.UNKNOWN


class VoiceTrigger(str, Enum):
    TOUCH = "touch"
    WAKE_WORD = "wake_word"
    HARDWARE_BUTTON = "hardware_button"


@dataclass(frozen=True)
class InteractionPolicy:
    motion: MotionState
    manual_text_enabled: bool
    rich_visual_interaction_enabled: bool
    voice_interaction_enabled: bool
    vehicle_write_enabled: bool
    reason: str


def policy_for(motion: MotionState) -> InteractionPolicy:
    if motion is MotionState.PARKED:
        return InteractionPolicy(
            motion=motion,
            manual_text_enabled=True,
            rich_visual_interaction_enabled=True,
            voice_interaction_enabled=True,
            vehicle_write_enabled=False,
            reason="Parked mode permits manual interaction; vehicle write remains disabled.",
        )

    reason = (
        "Moving mode restricts manual interaction."
        if motion is MotionState.MOVING
        else "Motion state is unknown, so AXLE applies moving-mode restrictions."
    )
    return InteractionPolicy(
        motion=motion,
        manual_text_enabled=False,
        rich_visual_interaction_enabled=False,
        voice_interaction_enabled=True,
        vehicle_write_enabled=False,
        reason=reason,
    )


def voice_trigger_allowed(policy: InteractionPolicy, trigger: VoiceTrigger) -> bool:
    if not policy.voice_interaction_enabled:
        return False
    if trigger is VoiceTrigger.TOUCH:
        return policy.motion is MotionState.PARKED
    return trigger in {VoiceTrigger.WAKE_WORD, VoiceTrigger.HARDWARE_BUTTON}
