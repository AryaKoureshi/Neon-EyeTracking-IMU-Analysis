import csv
import time
from datetime import datetime
import cv2

# Pupil Labs Neon real-time API
from pupil_labs.realtime_api.simple import (
    discover_one_device,
    Device
)


def connect_to_neon():
    """
    Attempt to discover a Neon device automatically.
    If discovery fails, manually provide an IP address.
    """
    try:
        print("Attempting to discover a Neon device on the local network...")
        device = discover_one_device()
        print("Successfully discovered a device.")
        return device
    except TimeoutError:
        print("Failed to discover a device automatically.")

        # Provide IP manually if discovery doesn't work:
        manual_ip = "neon.local"  # <-- Replace this with your phone’s IP
        port = "8080"
        print(f"Attempting to connect using IP {manual_ip}:{port}...")
        device = Device(address=manual_ip, port=port)
        print("Connected to Neon device via direct IP.")
        return device


def main():
    # 1. Connect to the Neon device
    device = connect_to_neon()

    # 2. Print out diagnostic info
    print(f"Phone IP address:   {device.phone_ip}")
    print(f"Phone name:         {device.phone_name}")
    print(f"Battery level:      {device.battery_level_percent}%")
    print(f"Free storage:       {device.memory_num_free_bytes / 1024**3:.1f} GB")
    print(f"Glasses serial:     {device.serial_number_glasses}")

    # 3. Start recording on the Neon device (remote side)
    recording_id = device.recording_start()
    print(f"Recording started on Neon with ID: {recording_id}")

    # Optionally send an event, e.g., "Experiment Start"
    device.send_event("Experiment Start")

    # 4. Prepare local CSV file to store gaze & IMU data
    data_filename = f"eye_data.csv"
    fieldnames = [
        "local_time",
        "scene_frame_timestamp_unix",
        "gaze_x",
        "gaze_y",
        "pupil_diameter_left",
        "pupil_diameter_right",
        "imu_timestamp_unix",
        "quaternion_x",
        "quaternion_y",
        "quaternion_z",
        "quaternion_w",
        "accel_x",
        "accel_y",
        "accel_z",
        "gyro_x",
        "gyro_y",
        "gyro_z"
    ]
    csv_file = open(data_filename, mode="w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # 5. Prepare local video writer for scene frames
    #    We'll grab one frame first to know resolution
    first_scene_sample, _ = device.receive_matched_scene_video_frame_and_gaze()
    height, width, _ = first_scene_sample.bgr_pixels.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'mp4v', 'MJPG', etc.
    fps = 25.0
    out_video = cv2.VideoWriter('output.avi', fourcc, fps, (width, height))

    cv2.namedWindow("Neon Live View", cv2.WINDOW_NORMAL)
    print("Press 'q' to quit live view...")

    while True:
        # 6. Receive matched scene frame & gaze data
        scene_sample, gaze_sample = device.receive_matched_scene_video_frame_and_gaze()
        frame_bgr = scene_sample.bgr_pixels
        
        # Get an IMU sample (might not arrive exactly at the same time as gaze_sample)
        # If you want perfectly matched IMU-to-gaze, you'll need to store timestamps and 
        # correlate them. For simplicity, we just read whenever available.
        imu_sample = device.receive_imu_datum()

        # 7. Draw optional gaze overlay on the scene
        if gaze_sample is not None:
            x, y = int(gaze_sample.x), int(gaze_sample.y)
            cv2.circle(frame_bgr, (x, y), 10, (0, 0, 255), 2)

        # 8. Show the scene video in a window
        #cv2.imshow("Neon Live View", frame_bgr)

        # Write the frame to our local video file
        out_video.write(frame_bgr)

        # 9. Collect data into dictionary for CSV
        # Get local PC time (e.g., for reference)
        local_timestamp = datetime.now().isoformat()

        data_row = {
            "local_time": local_timestamp,

            # Scene / Gaze
            "scene_frame_timestamp_unix": scene_sample.timestamp_unix_seconds,  # float
            "gaze_x": getattr(gaze_sample, "x", None),
            "gaze_y": getattr(gaze_sample, "y", None),
            "pupil_diameter_left": getattr(gaze_sample, "pupil_diameter_left", None),
            "pupil_diameter_right": getattr(gaze_sample, "pupil_diameter_right", None),

            # IMU
            "imu_timestamp_unix": getattr(imu_sample, "timestamp_unix_seconds", None),
            "quaternion_x": getattr(imu_sample.quaternion, "x", None) if imu_sample else None,
            "quaternion_y": getattr(imu_sample.quaternion, "y", None) if imu_sample else None,
            "quaternion_z": getattr(imu_sample.quaternion, "z", None) if imu_sample else None,
            "quaternion_w": getattr(imu_sample.quaternion, "w", None) if imu_sample else None,
            "accel_x": getattr(imu_sample.accel_data, "x", None) if imu_sample else None,
            "accel_y": getattr(imu_sample.accel_data, "y", None) if imu_sample else None,
            "accel_z": getattr(imu_sample.accel_data, "z", None) if imu_sample else None,
            "gyro_x": getattr(imu_sample.gyro_data, "x", None) if imu_sample else None,
            "gyro_y": getattr(imu_sample.gyro_data, "y", None) if imu_sample else None,
            "gyro_z": getattr(imu_sample.gyro_data, "z", None) if imu_sample else None
        }

        writer.writerow(data_row)
        csv_file.flush()  # Ensure data is written in real time

        # 10. Check for 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stopping live view...")
            break

    # 11. Stop and save the recording on Neon
    device.recording_stop_and_save()
    print("Stopped and saved recording on Neon device.")

    # 12. Close local resources
    out_video.release()
    csv_file.close()
    cv2.destroyAllWindows()

    print(f"Local CSV data saved in {data_filename}")
    print("Local video saved as 'scene_output.avi'")

if __name__ == "__main__":
    main()
