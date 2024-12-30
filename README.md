# Neon-EyeTracking-IMU-Analysis

A sample project demonstrating how to capture real-time video and gaze data using [Pupil Labs Neon](https://docs.pupil-labs.com/neon/) and subsequently analyze the recorded data with Python.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Code Explanation](#code-explanation)
  - [neon_data_collection.py](#1-neon_data_collectionpy)
  - [analysis_visualization.py](#2-analysis_visualizationpy)
- [License](#license)

---

## Overview

This repository demonstrates a simple workflow for:
1. Connecting to a Pupil Labs Neon device and starting a real-time data stream (video, gaze data, and IMU data).
2. Storing the data locally in a CSV file and saving a corresponding video file.
3. Loading that CSV file for analysis and visualization in Python, generating plots for gaze trajectories, pupil diameters, head orientation, and more.

---

## Features

- **Real-Time Neon Data Collection**: Connect automatically or manually to a Neon device.  
- **Local Recording**: Saves synchronized scene video, gaze, and IMU data.  
- **Data Visualization & Analysis**: Plots with Matplotlib and Plotly (3D scatter plots, Euler angles over time, heatmaps, and motion trails).  
- **Extensible**: Easily modify for your own experiments by adding more data streams or different analysis plots.

---

## Requirements

Below are the key dependencies:

- Python 3.7+  
- [pupil-labs-realtime-api](https://pypi.org/project/pupil-labs-realtime-api/)  
- OpenCV (e.g. `opencv-python`)  
- NumPy  
- Pandas  
- Matplotlib  
- Plotly  
- SciPy  

See [Installation](#installation) for details on how to set them up.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/AryaKoureshi/Neon-EyeTracking-IMU-Analysis.git
   cd Neon-EyeTracking-IMU-Analysis
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   This installs all required Python packages.

---

## Usage

1. **Connect to the Neon device**  
   - Ensure the Neon device is on the same network as your computer.  
   - If automatic discovery fails, edit the IP address in `neon_data_collection.py` in the `connect_to_neon()` function.

2. **Start Data Collection**:
   ```bash
   python neon_data_collection.py
   ```
   - This script will attempt to discover your Neon device.  
   - It starts recording on the Neon phone, saves the video locally (`output.avi`), and writes gaze & IMU data to `eye_data.csv`.
   - Press **q** to stop the live view and end the recording.

3. **Run Analysis & Visualization**:
   ```bash
   python analysis_visualization.py
   ```
   - This script reads `eye_data.csv` and generates various plots:  
     - Gaze trajectory  
     - Pupil diameters over time  
     - Head orientation (Euler angles)  
     - Gyroscope and accelerometer magnitudes  
   - Some plots are interactive (with Plotly).

4. **Review Outputs**  
   - **eye_data.csv**: Contains all relevant gaze, IMU, and timestamp data.  
   - **output.avi**: Local copy of the scene video.  
   - Various plots will appear on your screen, or you can save them to PNG/HTML (see last lines in `analysis_visualization.py`).

---

## Code Explanation

### 1) `neon_data_collection.py`

- **Imports**:  
  - `pupil_labs.realtime_api.simple` for connecting to the Neon device.  
  - `csv`, `time`, `datetime`, `cv2` for data formatting and video capturing.  

- **`connect_to_neon()`**:  
  - Discovers a Neon device automatically on the local network.  
  - If it fails, it attempts to connect using a manually provided IP address.

- **`main()`**:  
  - Connects to the Neon device.  
  - Prints diagnostic info (phone IP, battery, etc.).  
  - Starts recording on the Neon device.  
  - Sets up a local CSV file (`eye_data.csv`) and video writer (`output.avi`).  
  - Continuously receives synchronized scene frames and gaze data.  
  - Optionally overlays the gaze point on the scene video.  
  - Retrieves IMU data (gyroscope, accelerometer, quaternion) and logs it to CSV.  
  - Pressing **q** stops the loop, ending the local recording, and stops the Neon recording on the device.

This script demonstrates how to **capture real-time** gaze and IMU data from the Neon system, providing a foundation for eye-tracking experiments.

### 2) `analysis_visualization.py`

- **Imports**:  
  - `pandas`, `numpy`, `matplotlib`, `plotly.express` for data handling and visualization.  
  - `scipy.spatial.transform.Rotation` for converting quaternions to Euler angles.

- **Data Reading**:
  - Loads `eye_data.csv` into a DataFrame.  
  - Converts `local_time` to a proper datetime object for time-series plots.

- **Quaternion to Euler Angles**:  
  - Uses SciPy’s `Rotation.from_quat` to convert `[x, y, z, w]` into roll, pitch, and yaw angles.

- **Head Movement Metrics**:
  - Computes gyroscope magnitude (`sqrt(gyro_x^2 + gyro_y^2 + gyro_z^2)`), and similarly for accelerometer data.

- **Plotting**:
  - **3D Scatter**: Gaze X, Gaze Y, and pupil diameter in 3D (Matplotlib & Plotly).  
  - **Time Series**: Roll, pitch, yaw over time, as well as pupil diameters and gyroscope magnitude.  
  - **Heatmaps**: Shows how roll/pitch/yaw vary with gaze position.  
  - **Motion Trails**: Gaze trajectory over time.  
  - **Vector Fields**: Uses quiver plots to show head movement vectors.

This script provides a comprehensive set of **visual analytics** for understanding gaze behavior, pupil dynamics, and head movement.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Happy Tracking & Analysis!**

If you have any questions, feel free to open an issue or submit a pull request.
```
