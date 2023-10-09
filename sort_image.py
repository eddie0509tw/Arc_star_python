import re
import os
import shutil

def get_file_time(file_name):
    match = re.search(r'(\d+\.\d+)',file_name)
    if match:
        return float(match.group(1))
    else:
        raise Exception("Error: file name does not match the pattern")


def sort_directory(original_plot_path,path_to_plot):
    shutil.rmtree(path_to_plot)
    os.makedirs(path_to_plot,exist_ok=True)
    files = os.listdir(original_plot_path)
    sorted_images = sorted(files,key=get_file_time)

    for i in range(len(sorted_images)):
        new_file_name = "{:0>6d}.png".format(i)
        shutil.move(os.path.join(original_plot_path,sorted_images[i]),os.path.join(path_to_plot,new_file_name))
    
    shutil.rmtree(original_plot_path)
    return


    
if __name__ == '__main__':
    path = "./track_plot/"
    print(sorted(os.listdir(path),key=get_file_time))