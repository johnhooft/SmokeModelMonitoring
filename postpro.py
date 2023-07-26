import cv2
from matplotlib import pyplot as plt
import numpy as np
import os

def calculate_num_tiles(resize_dimensions, crop_height, tile_dimensions, tile_overlap):
    """Description: Give image size, calculates the number of tiles along the height and width
       Originally Written by: Anshuman Dewangan
    """
    num_tiles_height = 1 + (crop_height - tile_dimensions[0]) // (tile_dimensions[0] - tile_overlap)
    num_tiles_width = 1 + (resize_dimensions[1] - tile_dimensions[1]) // (tile_dimensions[1] - tile_overlap)
    
    return num_tiles_height, num_tiles_width

def calculate_overlap_ticks(max_dim, tile_size=224, tile_overlap=20):
    i = 0
    dim = 0
    ticks = []

    while dim < max_dim:
        if i == 0:
            dim += tile_size-tile_overlap
        elif i % 2 == 1:
            dim += tile_overlap
        elif i % 2 == 0:
            dim += tile_size-tile_overlap*2

        ticks.append(dim)
        i += 1
    
    return ticks

def reshape_tile_probs(tile_probs, num_tiles_height, num_tiles_width):
    return tile_probs.reshape(1, num_tiles_height, num_tiles_width)[0]


def drawtiles(data, file_name):

    resize_dimensions = (1392, 1856)
    crop_height = 1040
    tile_overlap = 20
    tile_dimensions = (224, 224)

    # reshape tile preds
    num_tiles_height, num_tiles_width = calculate_num_tiles(resize_dimensions, 
                                                                crop_height, 
                                                                tile_dimensions, 
                                                                tile_overlap)
    tile_probs = data.prob
    #convert tile_probs into a numpy array and then reshape it.
    tile_probs = np.reshape(tile_probs, (num_tiles_height, num_tiles_width))

    img = cv2.imread(file_name)
    img = cv2.resize(img, (resize_dimensions[1],resize_dimensions[0]))[-crop_height:]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(16, 12), dpi=80)
    plt.imshow(img)

    plt.xticks(calculate_overlap_ticks(resize_dimensions[1], tile_dimensions[1], tile_overlap), alpha=0)
    plt.yticks(calculate_overlap_ticks(crop_height, tile_dimensions[0], tile_overlap), alpha=0)
    plt.grid()


    x_text_ticks = np.insert(np.arange(tile_dimensions[1],resize_dimensions[1],tile_dimensions[1]-tile_overlap), 0, 0)
    y_text_ticks = np.insert(np.arange(tile_dimensions[0],crop_height,tile_dimensions[0]-tile_overlap), 0, 0)+tile_overlap

    for i, x in enumerate(x_text_ticks):
        for j, y in enumerate(y_text_ticks):
            if tile_probs is not None:
                plt.text(x,y, round(tile_probs[j,i], 2), size='medium', weight='heavy', color='white' if tile_probs[j,i]<0.75 else 'red')

    os.remove(file_name)
    newimage_name = "output_image.png"
    plt.savefig(newimage_name)
    print("Data Visualization Plot saved as 'output_image.png'.")
    return data.timestamp, newimage_name
