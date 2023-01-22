# Code for plotting original size/resolution of image from
# https://stackoverflow.com/questions/34768717/matplotlib-unable-to-save-image-in-same-resolution-as-original-image

import os
import matplotlib.pyplot as plt
import imageio
import pandas as pd
import os

font = {'family': 'sans-serif',
        'color':  'red',
        'weight': 'bold',
        'size': 50
        }

dpi = 96 # as original OSIRIS jpegs are
arrow_length = 200

data_path = '.'
match_set = "F22-phase-angle-25.0"
images_path = "downloaded_images"
destination_path = "subject-set-" + match_set

# http://foo.org/bla.jpg => downloaded_images/bla.jpg
def cached_filename_from_url(url):
    return images_path + "/" + os.path.basename(url)

# http://foo.org/bla.jpg => bla.jpg
def subject_filename_from_url(url):
    return os.path.basename(url)

# Put the filenames of each pair in a dataframe for future reference

df = pd.read_csv(os.path.join('.', 'matches-' + match_set + '.csv'))
df['pre'] = df['pre_browse_url'].apply(subject_filename_from_url)
df['post'] = df['post_browse_url'].apply(subject_filename_from_url)


# Draw an arrow to comet north on each image

def generate_subject_image(destination, north_vector, raw_image):
    im = imageio.imread(raw_image)
    
    # What size does the figure need to be in inches to fit the image?
    height, width, _colors = im.shape
    figsize = width / float(dpi), height / float(dpi)

    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.imshow(im, cmap="gray")
    ax.arrow(1700, 300, arrow_length * north_vector[0], arrow_length * north_vector[1], color=[1,1,0], head_width=50)
    fig.savefig(destination, dpi=dpi, transparent=True)
    plt.close(fig)


# Call arrow-drawing function for both pre and post image in each subject

def generate_subject_images(row):
    pre = destination_path + '/' + row['pre']
    if not os.path.exists(pre):
        pre_north_vector = [row['pre_vec1'], row['pre_vec2']]
        local_cached_filename = cached_filename_from_url(row['pre_browse_url'])
        generate_subject_image(pre, pre_north_vector, local_cached_filename)

    post = destination_path + '/' + row['post']
    if not os.path.exists(post):
        post_north_vector = [row['post_vec1'], row['post_vec2']]
        local_cached_filename = cached_filename_from_url(row['post_browse_url'])
        generate_subject_image(post, post_north_vector, local_cached_filename)

# Do all of the above for all subjects

for idx, row in df.iterrows():
    print(idx)
    generate_subject_images(row)


# Generate Zooniverse manifest file

manifest = df.copy()
manifest.pop('match_pre')
manifest.pop('match_post')
manifest.to_csv(destination_path + "/" + "manifest.csv", index=False)