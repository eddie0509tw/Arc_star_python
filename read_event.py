import numpy as np
import os
from arc_detector import ArcDetector
from arc_tracker import EventTracker
from sort_image import sort_directory
import cv2 as cv
import matplotlib.pyplot as plt
import argparse
import pdb

def load_event_file(file_path, n_event=2000000, expected_num_event=2000000):
    event_vec = []

    try:
        with open(file_path, 'r') as file:
            event_vec = []  # Event vec must be empty

            # Preallocate list
            event_vec = [None] * expected_num_event

            i_event = 0
            for line in file:
                if n_event != 0 and i_event >= n_event:
                    break  # Maximum number of events reached

                parts = line.split()
                if len(parts) != 4:
                    continue  # Skip lines that don't have 4 values

                t, x, y, p = map(float, parts)  # Convert string values to appropriate types

                event = (t, int(x), int(y), bool(p))
                event_vec[i_event] = event
                i_event += 1

    except FileNotFoundError:
        print("Error opening file")
        return None

    event_vec = np.array(event_vec[:i_event],dtype=np.float64)  # Trim the list to the actual number of events
    return event_vec

def load_img_file(dir_name,file_path, n_img=500):
    try:
        with open(file_path, 'r') as file:
            img_vec = []  # Event vec must be empty
            time_stamp_vec = []

            # Preallocate list
            img_vec = [None] * n_img
            time_stamp_vec = [None] * n_img

            i_img = 0
            for line in file:
                if n_img != 0 and i_img >= n_img:
                    break  # Maximum number of events reached
                seg = line.split()
                if len(seg) != 2:
                    continue
                time_stamp, img_name = seg[0], seg[1]
                img = cv.imread(os.path.join(os.path.dirname(dir_name), img_name))
                time_stamp_vec[i_img],img_vec[i_img] = time_stamp,img
                i_img += 1

    except FileNotFoundError:
        print("Error opening file")
        return None
    return time_stamp_vec[:i_img],img_vec[:i_img]

def plot_event_on_img(event_in_range,curr_corner,img,time_stamp, save_dir="./temp/", track_mode = True):
    # Create a Matplotlib figure and axis
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(img)

    # Plot the points as blue dots
    if track_mode:
        ax.plot(event_in_range[:, 1], event_in_range[:, 2], 'bo',markersize = 2)  # Blue dots for past trail
    ax.plot(curr_corner[:,1], curr_corner[:,2], 'ro',markersize = 2)  # Red dots


    # Specify the filename and extension (e.g., .png, .jpg, .pdf)
    file_name = 'time_{}.png'.format(time_stamp)

    # Combine the directory path and filename
    file_path = os.path.join(save_dir, file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Show the plot
    plt.savefig(file_path)
    plt.close()

if __name__ == '__main__':
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Description of your script.')

    # Add command-line arguments
    parser.add_argument('--mode', '-m',default=True ,type=bool, help='which mode to run, track or not')
    parser.add_argument('--input', '-i',default= './shapes_rotation/', type=str, help='Input file path')
    #parser.add_argument('--output', '-o', type=str, help='Output file path')
    #parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode')

    # Parse the command-line arguments
    args = parser.parse_args()

    __file__ = args.input
    event_file_path = os.path.join(os.path.dirname(__file__), 'events.txt')
    img_txtfile_path = os.path.join(os.path.dirname(__file__), 'images.txt')
    track_mode = args.mode


    time_stamp_vec,img_vec = load_img_file(__file__,img_txtfile_path)

    # print(time_stamp_vec[0])
    # print(img_vec[0].shape)

    event_vec = load_event_file(event_file_path)
    # print(event_vec)
    # print(event_vec.shape)
    detector = ArcDetector(img_vec[0])
    corner_index = []
    for i in range(len(event_vec)):
        corner_index.append(detector.detect_corner(event_vec[i,:]))
        detector.update(event_vec[i,:])

    corner_index = np.array(corner_index,dtype=np.bool_)
    # print(corner_index)
    # print(corner_index.shape)
    tracker = EventTracker()
    corners = event_vec[corner_index,:]
    last_t = corners[-1,0]
    active_branch = None
    for i in range(len(img_vec)):
        img = img_vec[i]
        time = float(time_stamp_vec[i])
        if time > last_t:
            break
        center = time
        points_in_range = corners[np.logical_and((corners[:,0] >= (center - 0.004)), (corners[:,0] < (center + 0.004)))]
        if track_mode:
            for j in range(points_in_range.shape[0]):
                tracker.add_corner_event(points_in_range[j,:])
            active_branch = tracker.pick_branch()
        # if i % 20000 == 0:
        #     pdb.set_trace()
        plot_event_on_img(active_branch,points_in_range,img,time,track_mode = track_mode)

    sort_directory("./temp/","./track_plot/")
    # print(corners)
    # print(corners.shape)
    # print(time)
    # print(points_in_range.shape)

