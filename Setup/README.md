# Setup and Calibration

This directory contains the requirements and tools for calibrating the AmazingHand servos.

## 1. Set up a Conda Environment (Recommended)

It is recommended to use a Conda environment to keep your dependencies isolated. 
You can create and activate a new Python environment using the following commands:

```bash
# Create a new conda environment named 'amazinghand' with Python 3.10 (or your preferred version)
conda create -n amazinghand python=3.10 -y

# Activate the environment
conda activate amazinghand
```

## 2. Install Requirements

Once your environment is active, install the required packages using `pip` and the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 3. Using the Calibration Tool (`calibrate_finger.py`)

The `calibrate_finger.py` script allows you to manually adjust and save the zero-point calibration for each servo. 
Make sure your controller is connected via USB (default: `/dev/ttyACM0`).

To run the tool:
```bash
python calibrate_finger.py
```

### Controls:
Once the script is running, it will load any previously saved calibration from `calibration.json`. You can interact with it using your keyboard:

- **`1` - `8`**: Select the active servo ID you want to calibrate.
- **`UP arrow`**: Increase the zero point of the active servo by 1 degree.
- **`DOWN arrow`**: Decrease the zero point of the active servo by 1 degree.
- **`m`**: Move the active servo to its middle (zero) position.
- **`o`**: Move the active servo to its open position.
- **`k`**: Move the active servo to its closed position.
- **`q`**: Save the current calibration to `calibration.json` and exit the program. 

**Note on errors:** If a servo with the selected ID is not found (for example if the external power isn't connected), the script will raise an opaque "Parsing error", like
```
    c.write_torque_enable(s_id, 1)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
RuntimeError: Parsing error
```

**Note on permissions:** If you encounter a permission error accessing `/dev/ttyACM0`, you may need to add your user to the `dialout` group (`sudo usermod -aG dialout $USER` and log out/in) or run the script with `sudo` (though using the `dialout` group is preferred).
