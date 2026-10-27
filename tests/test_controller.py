import unittest

from wind_turbine_ai import (
    DualVAWTController,
    GeneratorWiring,
    OperatingMode,
    SensorSnapshot,
)


class DualVAWTControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = DualVAWTController()

    def test_prefers_star_wiring_in_low_wind_blackout_mode(self) -> None:
        snapshot = SensorSnapshot(
            wind_speed_mph=12.0,
            gust_frequency_hz=0.8,
            turbine_a_rpm=48.0,
            turbine_b_rpm=50.0,
            generator_rpm=240.0,
            battery_soc=0.32,
            battery_voltage=50.2,
            battery_temp_c=22.0,
            mode=OperatingMode.BLACKOUT,
            grid_available=False,
        )

        command = self.controller.recommend(snapshot)

        self.assertEqual(command.generator_wiring, GeneratorWiring.STAR)
        self.assertFalse(command.emergency_brake)
        self.assertLess(command.brake_duty_cycle, 0.1)
        self.assertIn("battery-first operation", command.notes)

    def test_switches_to_delta_for_higher_rpm_generation(self) -> None:
        snapshot = SensorSnapshot(
            wind_speed_mph=28.0,
            gust_frequency_hz=1.5,
            turbine_a_rpm=94.0,
            turbine_b_rpm=90.0,
            generator_rpm=420.0,
            battery_soc=0.65,
            battery_voltage=53.8,
            battery_temp_c=24.0,
            mode=OperatingMode.GRID_TIED,
            grid_available=True,
        )

        command = self.controller.recommend(snapshot)

        self.assertEqual(command.generator_wiring, GeneratorWiring.DELTA)
        self.assertFalse(command.emergency_brake)
        self.assertGreaterEqual(command.transmission_ratio, 1.2)

    def test_engages_emergency_brake_at_sixty_mph(self) -> None:
        snapshot = SensorSnapshot(
            wind_speed_mph=60.0,
            gust_frequency_hz=2.0,
            turbine_a_rpm=130.0,
            turbine_b_rpm=132.0,
            generator_rpm=700.0,
            battery_soc=0.55,
            battery_voltage=54.0,
            battery_temp_c=25.0,
            mode=OperatingMode.GRID_TIED,
            grid_available=True,
        )

        command = self.controller.recommend(snapshot)

        self.assertTrue(command.emergency_brake)
        self.assertEqual(command.brake_duty_cycle, 1.0)
        self.assertEqual(command.generator_wiring, GeneratorWiring.STAR)

    def test_learning_profile_adjusts_follow_up_command(self) -> None:
        snapshot = SensorSnapshot(
            wind_speed_mph=24.0,
            gust_frequency_hz=1.0,
            turbine_a_rpm=82.0,
            turbine_b_rpm=84.0,
            generator_rpm=390.0,
            battery_soc=0.58,
            battery_voltage=52.5,
            battery_temp_c=23.0,
            mode=OperatingMode.GRID_TIED,
            grid_available=True,
        )

        initial = self.controller.recommend(snapshot)
        self.controller.record_outcome(
            snapshot,
            initial,
            measured_voltage=49.0,
            measured_power_watts=700.0,
        )
        learned = self.controller.recommend(snapshot)

        self.assertGreater(learned.transmission_ratio, initial.transmission_ratio)
        self.assertLess(learned.load_resistance_ohms, initial.load_resistance_ohms)

    def test_learning_profile_increases_braking_after_over_voltage(self) -> None:
        snapshot = SensorSnapshot(
            wind_speed_mph=26.0,
            gust_frequency_hz=1.0,
            turbine_a_rpm=104.0,
            turbine_b_rpm=106.0,
            generator_rpm=520.0,
            battery_soc=0.74,
            battery_voltage=55.2,
            battery_temp_c=24.0,
            mode=OperatingMode.GRID_TIED,
            grid_available=True,
        )

        initial = self.controller.recommend(snapshot)
        self.controller.record_outcome(
            snapshot,
            initial,
            measured_voltage=58.0,
            measured_power_watts=2400.0,
        )
        learned = self.controller.recommend(snapshot)

        self.assertGreater(learned.brake_duty_cycle, initial.brake_duty_cycle)

    def test_negative_gust_noise_shares_learning_bucket_with_zero_gust(self) -> None:
        noisy_snapshot = SensorSnapshot(
            wind_speed_mph=20.0,
            gust_frequency_hz=-0.1,
            turbine_a_rpm=72.0,
            turbine_b_rpm=74.0,
            generator_rpm=330.0,
            battery_soc=0.5,
            battery_voltage=52.0,
            battery_temp_c=21.0,
            mode=OperatingMode.BLACKOUT,
            grid_available=False,
        )

        zero_snapshot = SensorSnapshot(
            wind_speed_mph=20.0,
            gust_frequency_hz=0.0,
            turbine_a_rpm=72.0,
            turbine_b_rpm=74.0,
            generator_rpm=330.0,
            battery_soc=0.5,
            battery_voltage=52.0,
            battery_temp_c=21.0,
            mode=OperatingMode.BLACKOUT,
            grid_available=False,
        )

        initial_zero = self.controller.recommend(zero_snapshot)
        noisy_command = self.controller.recommend(noisy_snapshot)
        self.controller.record_outcome(
            noisy_snapshot,
            noisy_command,
            measured_voltage=49.0,
            measured_power_watts=800.0,
        )
        learned_zero = self.controller.recommend(zero_snapshot)

        self.assertGreater(
            learned_zero.transmission_ratio,
            initial_zero.transmission_ratio,
        )
        self.assertLess(
            learned_zero.load_resistance_ohms,
            initial_zero.load_resistance_ohms,
        )

    def test_learning_profile_reduces_braking_after_under_target_outcome(self) -> None:
        snapshot = SensorSnapshot(
            wind_speed_mph=26.0,
            gust_frequency_hz=1.0,
            turbine_a_rpm=104.0,
            turbine_b_rpm=106.0,
            generator_rpm=340.0,
            battery_soc=0.7,
            battery_voltage=55.0,
            battery_temp_c=24.0,
            mode=OperatingMode.GRID_TIED,
            grid_available=True,
        )

        initial = self.controller.recommend(snapshot)
        self.controller.record_outcome(
            snapshot,
            initial,
            measured_voltage=50.0,
            measured_power_watts=1800.0,
        )
        learned = self.controller.recommend(snapshot)

        self.assertLess(learned.brake_duty_cycle, initial.brake_duty_cycle)

    def test_grid_tied_without_grid_uses_lower_learning_target(self) -> None:
        grid_on_controller = DualVAWTController()
        grid_off_controller = DualVAWTController()

        grid_on_snapshot = SensorSnapshot(
            wind_speed_mph=24.0,
            gust_frequency_hz=1.0,
            turbine_a_rpm=82.0,
            turbine_b_rpm=84.0,
            generator_rpm=390.0,
            battery_soc=0.58,
            battery_voltage=52.5,
            battery_temp_c=23.0,
            mode=OperatingMode.GRID_TIED,
            grid_available=True,
        )
        grid_off_snapshot = SensorSnapshot(
            wind_speed_mph=24.0,
            gust_frequency_hz=1.0,
            turbine_a_rpm=82.0,
            turbine_b_rpm=84.0,
            generator_rpm=390.0,
            battery_soc=0.58,
            battery_voltage=52.5,
            battery_temp_c=23.0,
            mode=OperatingMode.GRID_TIED,
            grid_available=False,
        )

        grid_on_initial = grid_on_controller.recommend(grid_on_snapshot)
        grid_off_initial = grid_off_controller.recommend(grid_off_snapshot)

        grid_on_controller.record_outcome(
            grid_on_snapshot,
            grid_on_initial,
            measured_voltage=49.0,
            measured_power_watts=4300.0,
        )
        grid_off_controller.record_outcome(
            grid_off_snapshot,
            grid_off_initial,
            measured_voltage=49.0,
            measured_power_watts=4300.0,
        )

        grid_on_learned = grid_on_controller.recommend(grid_on_snapshot)
        grid_off_learned = grid_off_controller.recommend(grid_off_snapshot)

        self.assertGreater(
            grid_on_learned.transmission_ratio - grid_on_initial.transmission_ratio,
            grid_off_learned.transmission_ratio - grid_off_initial.transmission_ratio,
        )


if __name__ == "__main__":
    unittest.main()
