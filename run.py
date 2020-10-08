import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import PIL
from PIL import Image

"""
Usage Guideline:
    -> Define the directory (folder) in which this file (run.py) locates as the BASE_DIR
    -> Put images that need to be concatenated together into a folder, e.g "data_folder1". Thus the "data_folder1" has
    directory of "BASE_DIR/data_folder1"
    -> In command line terminal, navigate to the BASE_DIR, then run "python run.py data_folder1", then a image named
    "18-xxx_composite_image.tif" will be created within "BASE_DIR/"
"""

base_dir = "./"
# dist_pix_ratio = [[349, 702], [931, 1872]]
dist_pix_ratio = [[931, 1872], [349, 702]]

# Command Parameter Processing
if len(sys.argv):
    database_name = sys.argv[1]
    database_dir = os.path.join(base_dir, database_name)
    if not os.path.exists(database_dir):
        print("Unfound Data Folder")
        exit()
else:
    print("You Should Run Command[python run.py data_folder_name]")
    exit()

# Convert Distance Numeric Into Pixel Scale
def dist_to_pix(dist, axis=None):
    # axis = 0 (x-axis)
    # axis = 1 (y-axis)
    return round(float(dist) / dist_pix_ratio[axis][0] * dist_pix_ratio[axis][1])


print("--> Loading Images From '{}'...".format(database_dir))
image_groups = dict()
image_names = os.listdir(database_dir)
image_names = [image_name for image_name in image_names if image_name.endswith(".tif")]
for image_name in image_names:
    image_info = image_name.split("_")
    image_group, location = image_info[0], image_info[1]
    location = location[1:-1].split(",")
    location = [dist_to_pix(int(location[1]), axis=1), dist_to_pix(int(location[0]), axis=0)]
    image_data = plt.imread(os.path.join(database_dir, image_name))

    if image_group in image_groups:
        image_groups[image_group][0].append(image_name)
        image_groups[image_group][1][image_name] = location
        image_groups[image_group][2][image_name] = image_data
    else:
        image_groups[image_group] = [list(), dict(), dict()] # [locations, datas]
        image_groups[image_group][0].append(image_name)
        image_groups[image_group][1][image_name] = location
        image_groups[image_group][2][image_name] = image_data


for image_group in image_groups:
    print("=> Processing Image '{}'".format(image_group))
    print("--> Initializing Board")
    image_names, image_locations, image_datas = image_groups[image_group]
    all_locations = list(image_locations.values())
    max_loc_x = max(all_locations, key=lambda x: x[0])[0]
    max_loc_y = max(all_locations, key=lambda x: x[1])[1]
    min_loc_x = min(all_locations, key=lambda x: x[0])[0]
    min_loc_y = min(all_locations, key=lambda x: x[1])[1]
    all_shapes = [x.shape for x in list(image_datas.values())]
    max_shape_x = max(all_shapes, key=lambda x: x[0])[0]
    max_shape_y = max(all_shapes, key=lambda x: x[1])[1]
    min_shape_x = min(all_shapes, key=lambda x: x[0])[0]
    min_shape_y = min(all_shapes, key=lambda x: x[1])[1]
    board = np.zeros([max_loc_x - min_loc_x + max_shape_x * 2, max_loc_y - min_loc_y + max_shape_y * 2, 3], np.uint8)

    print("--> Concatenating Images...")
    for image_name in image_names:
        image_data = image_datas[image_name]
        image_location = image_locations[image_name]
        image_shape = image_data.shape

        #######################################################################################
        """
        DEBUG: Show Contour
        """
        # print(image_name, image_location, image_shape)
        # image_data = image_data.copy()
        #
        # image_data[0, :, :] = 255 * np.ones([image_shape[1], image_shape[2]], image_data.dtype)
        # image_data[-1, :, :] = 255 * np.ones([image_shape[1], image_shape[2]], image_data.dtype)
        # image_data[:, 0, :] = 255 * np.ones([image_shape[0], image_shape[2]], image_data.dtype)
        # image_data[:, -1, :] = 255 * np.ones([image_shape[0], image_shape[2]], image_data.dtype)

        #######################################################################################

        board[image_location[0]-min_loc_x-round(image_shape[0] / 2)+max_shape_x:image_location[0]-min_loc_x+round(image_shape[0] / 2)+max_shape_x, image_location[1]-min_loc_y-round(image_shape[1] / 2)+max_shape_y:image_location[1]-min_loc_y+round(image_shape[1] / 2)+max_shape_y] = \
            board[image_location[0]-min_loc_x-round(image_shape[0] / 2)+max_shape_x:image_location[0]-min_loc_x+round(image_shape[0] / 2)+max_shape_x, image_location[1]-min_loc_y-round(image_shape[1] / 2)+max_shape_y:image_location[1]-min_loc_y+round(image_shape[1] / 2)+max_shape_y] + \
            image_data

    print("--> Saving Image As '{}'".format(os.path.join(base_dir, "{}_composite_image.tif".format(image_group))))
    Image.fromarray(board).save(os.path.join(base_dir, "{}_composite_image.tif".format(image_group)))
