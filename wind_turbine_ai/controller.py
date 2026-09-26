from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


class GeneratorWiring(str, Enum):
    STAR = "star"
    DELTA = "delta"


class OperatingMode(str, Enum):
    BLACKOUT = "blackout"
    GRID_TIED = "grid_tied"


@dataclass(frozen=True)
class SensorSnapshot:
    wind_speed_mph: float
    gust_frequency_hz: float
    turbine_a_rpm: float
    turbine_b_rpm: float
    generator_rpm: float
    battery_soc: float
    battery_voltage: float
    battery_temp_c: float
    mode: OperatingMode
    grid_available: bool
    vibration_g: float = 0.0


@dataclass(frozen=True)
class ControlCommand:
    transmission_ratio: float
    generator_wiring: GeneratorWiring
    brake_duty_cycle: float
    load_resistance_ohms: float
    emergency_brake: bool
    notes: tuple[str, ...] = ()


@dataclass
class LearnedAdjustment:
    transmission_bias: float = 0.0
    resistance_bias: float = 0.0
    brake_bias: float = 0.0


@dataclass
class DualVAWTController:
    target_battery_voltage: float = 54.4
    target_generator_rpm: float = 380.0
    learned_adjustments: dict[tuple[int, int], LearnedAdjustment] = field(
        default_factory=dict
    )

    def recommend(self, snapshot: SensorSnapshot) -> ControlCommand:
        average_turbine_rpm = (snapshot.turbine_a_rpm + snapshot.turbine_b_rpm) / 2
        learned = self.learned_adjustments.get(
            self._profile_key(snapshot), LearnedAdjustment()
        )

        if self._is_emergency(snapshot):
            return ControlCommand(
                transmission_ratio=0.6,
                generator_wiring=GeneratorWiring.STAR,
                brake_duty_cycle=1.0,
                load_resistance_ohms=0.5,
                emergency_brake=True,
                notes=("emergency brake engaged",),
            )

        target_turbine_rpm = _clamp(
            30 + (snapshot.wind_speed_mph * 2.25) - (snapshot.gust_frequency_hz * 4.0),
            30.0,
            120.0,
        )
        transmission_ratio = _clamp(
            (self.target_generator_rpm / max(average_turbine_rpm, 1.0))
            + learned.transmission_bias,
            1.2,
            6.0,
        )

        rpm_error = target_turbine_rpm - average_turbine_rpm
        battery_margin = snapshot.battery_voltage - self.target_battery_voltage
        load_resistance = _clamp(
            5.0
            + (rpm_error * 0.05)
            + max(0.0, battery_margin) * 0.8
            + learned.resistance_bias,
            0.5,
            25.0,
        )

        brake_duty_cycle = _clamp(
            max(0.0, (average_turbine_rpm - target_turbine_rpm) / max(target_turbine_rpm, 1.0))
            + max(0.0, battery_margin) * 0.04
            + learned.brake_bias,
            0.0,
            1.0,
        )

        generator_wiring = (
            GeneratorWiring.STAR
            if snapshot.generator_rpm < 320
            or snapshot.wind_speed_mph < 18
            or snapshot.battery_soc < 0.35
            else GeneratorWiring.DELTA
        )

        notes = []
        if snapshot.mode is OperatingMode.BLACKOUT or not snapshot.grid_available:
            notes.append("battery-first operation")
        if snapshot.wind_speed_mph >= 45:
            notes.append("high-wind stability mode")
        if battery_margin > 0:
            notes.append("battery protection active")

        return ControlCommand(
            transmission_ratio=round(transmission_ratio, 3),
            generator_wiring=generator_wiring,
            brake_duty_cycle=round(brake_duty_cycle, 3),
            load_resistance_ohms=round(load_resistance, 3),
            emergency_brake=False,
            notes=tuple(notes),
        )

    def record_outcome(
        self,
        snapshot: SensorSnapshot,
        command: ControlCommand,
        measured_voltage: float,
        measured_power_watts: float,
    ) -> None:
        if command.emergency_brake:
            return

        profile = self.learned_adjustments.setdefault(
            self._profile_key(snapshot), LearnedAdjustment()
        )
        target_power = self._target_power(snapshot)
        power_gap = target_power - measured_power_watts
        voltage_gap = measured_voltage - self.target_battery_voltage

        transmission_step = _clamp(-power_gap / 3000.0, -0.2, 0.2)
        if command.transmission_ratio >= 5.5 and transmission_step > 0:
            transmission_step *= 0.5
        if command.transmission_ratio <= 1.5 and transmission_step < 0:
            transmission_step *= 0.5

        resistance_step = _clamp(
            (-power_gap / 2500.0) + (voltage_gap * 0.5), -2.0, 2.0
        )
        if command.load_resistance_ohms <= 1.0 and resistance_step < 0:
            resistance_step = 0.0

        brake_step = _clamp(
            max(0.0, voltage_gap) * 0.08
            + max(0.0, snapshot.generator_rpm - self.target_generator_rpm) / 800.0,
            -0.1,
            0.2,
        )
        if command.brake_duty_cycle >= 0.9 and brake_step > 0:
            brake_step *= 0.5

        profile.transmission_bias = _clamp(
            profile.transmission_bias + transmission_step,
            -1.0,
            1.0,
        )
        profile.resistance_bias = _clamp(
            profile.resistance_bias + resistance_step,
            -8.0,
            8.0,
        )
        profile.brake_bias = _clamp(
            profile.brake_bias + brake_step,
            -0.5,
            0.8,
        )

    def _is_emergency(self, snapshot: SensorSnapshot) -> bool:
        return any(
            (
                snapshot.wind_speed_mph >= 60.0,
                snapshot.turbine_a_rpm >= 180.0,
                snapshot.turbine_b_rpm >= 180.0,
                snapshot.generator_rpm >= 900.0,
                snapshot.vibration_g >= 2.5,
                snapshot.battery_temp_c >= 55.0,
            )
        )

    def _profile_key(self, snapshot: SensorSnapshot) -> tuple[int, int]:
        return (int(snapshot.wind_speed_mph // 5), int(snapshot.gust_frequency_hz // 1))

    def _target_power(self, snapshot: SensorSnapshot) -> float:
        mode_multiplier = 0.85 if snapshot.mode is OperatingMode.BLACKOUT else 1.0
        return _clamp((snapshot.wind_speed_mph**2) * 8.5 * mode_multiplier, 250.0, 6500.0)
