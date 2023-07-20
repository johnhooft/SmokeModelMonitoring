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

resize_dimensions = (1392, 1856)
crop_height = 1040
tile_overlap = 20
tile_dimensions = (224, 224)

# reshape tile preds
num_tiles_height, num_tiles_width = calculate_num_tiles(resize_dimensions, 
                                                            crop_height, 
                                                            tile_dimensions, 
                                                            tile_overlap)

tile_preds = tile_preds.reshape(1,num_tiles_height, num_tiles_width)[0]
tile_probs = tile_probs.reshape(1,num_tiles_height, num_tiles_width)[0]

img = cv2.imread(current_image_path)
img = cv2.resize(img, (resize_dimensions[1],resize_dimensions[0]))[-crop_height:]
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(16, 12), dpi=80)
plt.imshow(img)

plt.xticks(calculate_overlap_ticks(resize_dimensions[1], tile_dimensions[1], tile_overlap), alpha=0)
plt.yticks(calculate_overlap_ticks(crop_height, tile_dimensions[0], tile_overlap), alpha=0)
plt.grid()


x_text_ticks = np.insert(np.arange(tile_dimensions[1],resize_dimensions[1],tile_dimensions[1]-tile_overlap), 0, 0)
y_text_ticks = np.insert(np.arange(tile_dimensions[0],crop_height,tile_dimensions[0]-tile_overlap), 0, 0)+tile_overlap

print(x_text_ticks)
print(y_text_ticks)

for i, x in enumerate(x_text_ticks):
    for j, y in enumerate(y_text_ticks):
        if tile_preds is not None:
            plt.text(x,y, tile_preds[j,i], size='medium', weight='heavy', color='white' if tile_preds[j,i]==0 else 'red')
        else:
            plt.text(x,y, round(tile_probs[j,i], 2), size='medium', weight='heavy', color='white' if tile_probs[j,i]<0.5 else 'red')
