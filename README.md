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

### Mechanical build sequence

1. Build the two VAWT assemblies with matching height, blade count, and airfoil geometry
   so both rotors have comparable inertia and aerodynamic response.
2. Confirm the blade attachment hardware, shaft alignment, and bearing supports are
   consistent between both turbines before connecting them together.
3. Mount both turbines on independent, rigid supports sized for gusts up to and above the
   intended 60 mph operating envelope, with enough clearance to avoid tower, chain, or
   blade interference.
4. Couple both turbines through the shared chain and transmission so the generator can be
   driven while still allowing ratio changes for RPM optimization.
5. Verify the chain path, sprocket alignment, tensioning, and guarding before any powered
   rotation tests.

### Sensors and controllable hardware

6. Install sensors for wind speed, gust frequency, turbine RPM, generator RPM, battery
   voltage, battery temperature, and vibration.
7. Place RPM and vibration sensors where they can be read repeatedly under load without
   contacting moving parts.
8. Wire controllable hardware interfaces for:
   - transmission or ratio control
   - generator star/delta switching
   - emergency electronic braking
   - adjustable dump/load resistance for amperage and RPM control
9. Label all sensor inputs and control outputs so the software-to-hardware mapping is easy
   to audit during setup and troubleshooting.

### Electrical integration and first startup

10. Connect the battery system and any grid-tied inverter equipment only after verifying
   voltage, current, grounding, overcurrent protection, and shutdown behavior.
11. Confirm the star/delta switching hardware cannot energize conflicting contactors at the
    same time.
12. Test emergency braking, manual shutdown, and no-load spin behavior before enabling
    automatic control.
13. Perform the first automatic runs with conservative load settings and direct supervision.

## Install the software

1. Install Python 3.12 or newer.
2. Clone the repository:

   ```bash
   git clone https://github.com/keithevin722-cell/keithevinwindturbineai.git
   cd keithevinwindturbineai
   ```

3. Sync your local `main` branch before making or deploying changes:

   ```bash
   git checkout main
   git pull origin main
   ```

4. Optionally create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

5. Confirm Python can import the package from the repository root:

   ```bash
   python -c "from wind_turbine_ai import DualVAWTController; print(DualVAWTController.__name__)"
   ```

6. Run the tests:

   ```bash
   python -m unittest discover -s tests
   ```

7. Copy or deploy the repository onto the computer or embedded Linux device that will read
   the sensors and drive relays, braking electronics, and load controls.
8. Import `DualVAWTController` into the Python process that runs each control cycle.

## Install into a control system

1. Create a hardware adapter layer that converts live field wiring and sensor values into
   software inputs and converts controller outputs into safe relay, contactor, PWM, or
   resistance commands.
2. Read live sensor data and map it into a `SensorSnapshot`.
3. Call `controller.recommend(snapshot)` on each control cycle.
4. Translate the returned `ControlCommand` into hardware actions:
   - transmission ratio adjustment
   - star/delta contactor selection
   - brake duty cycle output
   - load resistance setting
5. Add interlocks so emergency braking overrides normal ratio and load adjustments.
6. Log each snapshot, command, measured voltage, measured power, and safety event so you can
   review learning behavior over time.
7. After each cycle or test window, call `record_outcome(...)` with measured voltage and
   power so the controller can adapt by wind/gust bucket.
8. Start in supervised/manual mode and confirm emergency-brake behavior before allowing
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

Use `main` as the branch you sync from, then push changes from a feature branch for review:

```bash
git checkout main
git pull origin main
git checkout -b update-build-docs
git status
git add README.md
git commit -m "Update build and installation details"
git push -u origin update-build-docs
```

Then open a pull request and merge the approved change back into `main`.

If you only changed documentation, you can limit the add step:

```bash
git checkout main
git pull origin main
git checkout -b expand-readme-details
git add README.md
git commit -m "Expand README installation details"
git push -u origin expand-readme-details
```
