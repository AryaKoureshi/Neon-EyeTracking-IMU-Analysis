import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px

# 1. Read the CSV file
df = pd.read_csv("eye_data.csv")

# Convert 'local_time' to datetime
df['local_time_dt'] = pd.to_datetime(df['local_time'])

# 2. Convert Quaternion to Euler Angles
def quaternion_to_euler(x, y, z, w):
    r = R.from_quat([x, y, z, w])
    return r.as_euler('xyz', degrees=True)

euler_angles = df.apply(
    lambda row: quaternion_to_euler(
        row['quaternion_x'],
        row['quaternion_y'],
        row['quaternion_z'],
        row['quaternion_w']
    ), axis=1
)

df[['roll', 'pitch', 'yaw']] = pd.DataFrame(euler_angles.tolist(), index=df.index)

# 3. Calculate Head Movement Metrics
df['gyro_magnitude'] = np.sqrt(df['gyro_x']**2 + df['gyro_y']**2 + df['gyro_z']**2)
df['accel_magnitude'] = np.sqrt(df['accel_x']**2 + df['accel_y']**2 + df['accel_z']**2)

# 4. Plotting

# Initialize the figure
fig = plt.figure(figsize=(20, 15))

# 4.1. 3D Scatter Plot: Gaze X, Gaze Y, Pupil Diameter Left
ax1 = fig.add_subplot(221, projection='3d')
scatter = ax1.scatter(
    df['gaze_x'],
    df['gaze_y'],
    df['pupil_diameter_left'],
    c=df['pupil_diameter_left'],
    cmap='viridis',
    alpha=0.7,
    s=20
)
ax1.set_xlabel("Gaze X")
ax1.set_ylabel("Gaze Y")
ax1.set_zlabel("Pupil Diameter (Left)")
ax1.set_title("3D Scatter Plot: Gaze and Pupil Diameter")
cbar = fig.colorbar(scatter, ax=ax1, shrink=0.5, aspect=10)
cbar.set_label("Pupil Diameter (Left)")

# 4.2. Euler Angles Over Time
ax2 = fig.add_subplot(222)
ax2.plot(df['local_time_dt'], df['roll'], label='Roll')
ax2.plot(df['local_time_dt'], df['pitch'], label='Pitch')
ax2.plot(df['local_time_dt'], df['yaw'], label='Yaw')
ax2.set_xlabel("Local Time")
ax2.set_ylabel("Angle (degrees)")
ax2.set_title("Head Orientation Over Time")
ax2.legend()
ax2.grid(True)

# 4.3. Head Rotation Speed Over Time
ax3 = fig.add_subplot(223)
ax3.plot(df['local_time_dt'], df['gyro_magnitude'], color='r')
ax3.set_xlabel("Local Time")
ax3.set_ylabel("Gyroscope Magnitude (deg/s)")
ax3.set_title("Head Rotation Speed Over Time")
ax3.grid(True)

# 4.4. Combined Plot: Head Orientation & Rotation Speed
ax4 = fig.add_subplot(224)
ax4.plot(df['local_time_dt'], df['roll'], label='Roll')
ax4.plot(df['local_time_dt'], df['pitch'], label='Pitch')
ax4.plot(df['local_time_dt'], df['yaw'], label='Yaw')
ax4.set_xlabel("Local Time")
ax4.set_ylabel("Angle (degrees)")
ax4.set_title("Head Orientation & Rotation Speed")
ax4.legend(loc='upper left')
ax4_twin = ax4.twinx()
ax4_twin.plot(df['local_time_dt'], df['gyro_magnitude'], color='r', label='Gyro Magnitude')
ax4_twin.set_ylabel("Gyroscope Magnitude (deg/s)")
ax4_twin.legend(loc='upper right')
ax4.grid(True)

plt.tight_layout()
plt.show()

# 5. Interactive 3D Scatter Plot with Plotly
fig_plotly = px.scatter_3d(
    df,
    x='gaze_x',
    y='gaze_y',
    z='pupil_diameter_left',
    color='pupil_diameter_left',
    labels={
        'gaze_x': 'Gaze X',
        'gaze_y': 'Gaze Y',
        'pupil_diameter_left': 'Pupil Diameter (Left)'
    },
    title="Interactive 3D Scatter Plot: Gaze and Pupil Diameter",
    opacity=0.7
)

fig_plotly.show()

# 6. Heatmaps for Euler Angles
fig2, ax_heat = plt.subplots(3, 1, figsize=(15, 20), sharex=True)

# Heatmap for Roll
heat_roll = ax_heat[0].scatter(
    df['gaze_x'],
    df['gaze_y'],
    c=df['roll'],
    cmap='coolwarm',
    alpha=0.7,
    s=20
)
ax_heat[0].set_xlabel("Gaze X")
ax_heat[0].set_ylabel("Gaze Y")
ax_heat[0].set_title("Roll Heatmap")
cbar_roll = fig2.colorbar(heat_roll, ax=ax_heat[0])
cbar_roll.set_label("Roll (degrees)")

# Heatmap for Pitch
heat_pitch = ax_heat[1].scatter(
    df['gaze_x'],
    df['gaze_y'],
    c=df['pitch'],
    cmap='coolwarm',
    alpha=0.7,
    s=20
)
ax_heat[1].set_xlabel("Gaze X")
ax_heat[1].set_ylabel("Gaze Y")
ax_heat[1].set_title("Pitch Heatmap")
cbar_pitch = fig2.colorbar(heat_pitch, ax=ax_heat[1])
cbar_pitch.set_label("Pitch (degrees)")

# Heatmap for Yaw
heat_yaw = ax_heat[2].scatter(
    df['gaze_x'],
    df['gaze_y'],
    c=df['yaw'],
    cmap='coolwarm',
    alpha=0.7,
    s=20
)
ax_heat[2].set_xlabel("Gaze X")
ax_heat[2].set_ylabel("Gaze Y")
ax_heat[2].set_title("Yaw Heatmap")
cbar_yaw = fig2.colorbar(heat_yaw, ax=ax_heat[2])
cbar_yaw.set_label("Yaw (degrees)")

plt.tight_layout()
plt.show()

# 7. Motion Trails for Gaze
plt.figure(figsize=(10, 8))
plt.scatter(df['gaze_x'], df['gaze_y'], c=df['pupil_diameter_left'], cmap='viridis', alpha=0.6, s=10)
plt.plot(df['gaze_x'], df['gaze_y'], color='gray', alpha=0.3)  # Motion trail
plt.xlabel("Gaze X")
plt.ylabel("Gaze Y")
plt.title("Gaze Trajectory with Pupil Diameter")
plt.colorbar(label="Pupil Diameter (Left)")
plt.show()

# 8. Vector Field for Head Movements
plt.figure(figsize=(10, 8))

# Sample every nth point for clarity
n = 50
plt.quiver(
    df['gaze_x'][::n],
    df['gaze_y'][::n],
    df['gyro_x'][::n],
    df['gyro_y'][::n],
    df['gyro_magnitude'][::n],
    cmap='autumn',
    scale=50,
    width=0.003
)

plt.xlabel("Gaze X")
plt.ylabel("Gaze Y")
plt.title("Head Movement Vectors")
plt.colorbar(label="Gyroscope Magnitude (deg/s)")
plt.show()

# 9. Time-Series Analysis with Subplots
fig3, axs = plt.subplots(4, 1, figsize=(15, 20), sharex=True)

# Gaze Coordinates
axs[0].plot(df['local_time_dt'], df['gaze_x'], label='Gaze X')
axs[0].plot(df['local_time_dt'], df['gaze_y'], label='Gaze Y')
axs[0].set_ylabel("Gaze Position")
axs[0].set_title("Gaze Coordinates Over Time")
axs[0].legend()
axs[0].grid(True)

# Pupil Diameters
axs[1].plot(df['local_time_dt'], df['pupil_diameter_left'], label='Pupil Diameter Left')
axs[1].plot(df['local_time_dt'], df['pupil_diameter_right'], label='Pupil Diameter Right')
axs[1].set_ylabel("Pupil Diameter")
axs[1].set_title("Pupil Diameters Over Time")
axs[1].legend()
axs[1].grid(True)

# Euler Angles
axs[2].plot(df['local_time_dt'], df['roll'], label='Roll')
axs[2].plot(df['local_time_dt'], df['pitch'], label='Pitch')
axs[2].plot(df['local_time_dt'], df['yaw'], label='Yaw')
axs[2].set_ylabel("Angle (degrees)")
axs[2].set_title("Head Orientation Over Time")
axs[2].legend()
axs[2].grid(True)

# Gyroscope Magnitude
axs[3].plot(df['local_time_dt'], df['gyro_magnitude'], label='Gyro Magnitude', color='r')
axs[3].set_xlabel("Local Time")
axs[3].set_ylabel("Gyroscope Magnitude (deg/s)")
axs[3].set_title("Head Rotation Speed Over Time")
axs[3].legend()
axs[3].grid(True)

plt.tight_layout()
plt.show()

# 10. Save Plots (Optional)
# Uncomment the following lines to save the figures
# fig.savefig("Comprehensive_EyeTracking_IMU_Plots.png")
# fig2.savefig("Euler_Angles_Heatmaps.png")
# fig3.savefig("Time_Series_Analysis.png")
# fig_plotly.write_html("Interactive_3D_Scatter_Gaze_Pupil.html")
