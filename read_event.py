import numpy as np
import os
def load_event_file(file_path, n_event=3000000, expected_num_event=3000000):
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

if __name__ == '__main__':
    file_path = os.path.join(os.path.dirname(__file__), 'events.txt')
    event_vec = load_event_file(file_path)
    print(event_vec)
    print(event_vec.shape)