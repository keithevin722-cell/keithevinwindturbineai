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

## Build and install the equipment

> This repository provides control software logic only. Mechanical construction,
> high-current wiring, braking circuits, battery systems, and grid interconnection
> should be reviewed by qualified mechanical and electrical professionals before use.

1. Build the two VAWT assemblies with matching height, blade count, and airfoil geometry.
2. Mount both turbines on independent, rigid supports sized for gusts up to and above the
   intended 60 mph operating envelope.
3. Couple both turbines through the shared chain and transmission so the generator can be
   driven while still allowing ratio changes for RPM optimization.
4. Install sensors for wind speed, gust frequency, turbine RPM, generator RPM, battery
   voltage, battery temperature, and vibration.
5. Wire controllable hardware interfaces for:
   - transmission or ratio control
   - generator star/delta switching
   - emergency electronic braking
   - adjustable dump/load resistance for amperage and RPM control
6. Connect the battery system and any grid-tied inverter equipment only after verifying
   voltage, current, grounding, overcurrent protection, and shutdown behavior.
7. Perform dry-run checks with the generator unloaded before enabling automatic control.

## Install the software

1. Install Python 3.12 or newer.
2. Clone the repository:

   ```bash
   git clone https://github.com/keithevin722-cell/keithevinwindturbineai.git
   cd keithevinwindturbineai
   ```

3. Optionally create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

4. Run the tests:

   ```bash
   python -m unittest discover -s tests
   ```

5. Import `DualVAWTController` into the computer or embedded Python environment that will
   read sensor values and issue commands to relays, braking electronics, and load controls.

## Install into a control system

1. Read live sensor data and map it into a `SensorSnapshot`.
2. Call `controller.recommend(snapshot)` on each control cycle.
3. Translate the returned `ControlCommand` into hardware actions:
   - transmission ratio adjustment
   - star/delta contactor selection
   - brake duty cycle output
   - load resistance setting
4. After each cycle or test window, call `record_outcome(...)` with measured voltage and
   power so the controller can adapt by wind/gust bucket.
5. Start in supervised/manual mode and confirm emergency-brake behavior before allowing
   unattended operation.

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

## Push updates

After making documentation or code changes locally:

```bash
git status
git add README.md wind_turbine_ai tests
git commit -m "Describe build and installation workflow"
git push
```
