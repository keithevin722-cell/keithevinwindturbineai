# keithevinwindturbineai

Minimal Python control logic for a dual-VAWT wind system with:

- two 6' VAWTs with three NACA 0018 airfoils each
- transmission ratio control between the turbines and generator
- generator star/delta switching
- emergency electronic braking for high-wind protection
- adjustable electrical load resistance for RPM and amperage control
- adaptive learning that nudges future setpoints by wind-speed and gust profile

The controller is intentionally small and dependency-free so it can serve as a starting
point for hardware integration.

## Usage

```python
from wind_turbine_ai import DualVAWTController, OperatingMode, SensorSnapshot

controller = DualVAWTController()
snapshot = SensorSnapshot(
    wind_speed_mph=22.0,
    gust_frequency_hz=1.2,
    turbine_a_rpm=78.0,
    turbine_b_rpm=80.0,
    generator_rpm=360.0,
    battery_soc=0.61,
    battery_voltage=53.4,
    battery_temp_c=24.0,
    mode=OperatingMode.BLACKOUT,
    grid_available=False,
)

command = controller.recommend(snapshot)
controller.record_outcome(snapshot, command, measured_voltage=53.0, measured_power_watts=1800.0)
```

## Behavior

- prefers battery-first operation during blackout conditions
- switches to star wiring at lower generator RPM and delta at higher RPM
- engages emergency braking at 60+ mph wind, 180+ turbine RPM, 900+ generator RPM, 2.5+ g vibration, or 55+ °C battery temperature
- stores learned transmission, resistance, and braking offsets by wind/gust bucket

## Testing

```bash
python -m unittest discover -s tests
```
