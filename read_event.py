import numpy as np
import os
import arc_detector
import cv2 as cv
def load_event_file(file_path, n_event=300000, expected_num_event=300000):
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

    event_vec = np.array(event_vec[:i_event],dtype=np.int32)  # Trim the list to the actual number of events
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

if __name__ == '__main__':
    __file__ = './shapes_rotation/'
    event_file_path = os.path.join(os.path.dirname(__file__), 'events.txt')
    img_txtfile_path = os.path.join(os.path.dirname(__file__), 'images.txt')


    time_stamp_vec,img_vec = load_img_file(__file__,img_txtfile_path)
    print(time_stamp_vec[0])
    print(img_vec[0].shape)

    event_vec = load_event_file(event_file_path)
    print(event_vec)
    print(event_vec.shape)
    detector = arc_detector.ArcDetector(img_vec[0])
    corner_index = []
    for i in range(len(event_vec)):
        corner_index.append(detector.detect_corner(event_vec[i,:]))
    corner_index = np.array(corner_index,dtype=np.bool_)
    print(corner_index)
    print(corner_index.shape)

    corners = event_vec[corner_index,:]
    print(corners)
    print(corners.shape)

