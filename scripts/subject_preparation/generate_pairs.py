# This code is adapted from rosetta_zoo_pairs.ipynb: https://github.com/msbentley/osiris_zoo/blob/bffd2d7506a8297cf01011198cd2196eb658a69e/rosetta_zoo_pairs.ipynb
# Needs osinac_metadata_orientation.csv.gz, get this from https://github.com/msbentley/osiris_zoo/blob/bffd2d7506a8297cf01011198cd2196eb658a69e/osinac_metadata.csv.gz

import math
import os
import pandas as pd

data_path = '.'
MAX_PHASE_DIFFERENCE = 25.

# Load the data

images = pd.read_csv(os.path.join(data_path, 'osinac_metadata_orientation.csv.gz'))
images = images[images.prod_id.str.contains('F22.FIT')]

# Correctly format the timestamps and divide the data into two sets, in this case pre-perihelion and post-perihelion

images.start_time = pd.to_datetime(images.start_time)
images.stop_time = pd.to_datetime(images.stop_time)

t_perihelion = pd.Timestamp('2015-08-13T02:03:00Z').to_datetime64()

pre = images[images.start_time<t_perihelion]
post = images[images.start_time>=t_perihelion]


# Define a simple function to check for possible pairs:
# - check that the distance between the boresight intercepts is < half the first image width
# - put some constraints on the phase angle and and field of view etc.

# This is where "the magic" happens, so this should be tweaked as needed to get optimal pairs
# This now returns the indices of the best match and the distance between the intercept points on the comet

def best_match(df1, df2, idx1):
    matches = []
    distance = []
    if idx1 not in df1.index:
        print('no matching index in df1')
        return None, None
    img = df1.loc[idx1]
    for idx, match in df2.iterrows():
        
        dist = math.sqrt( (match.surf_int_x-img.surf_int_x)**2 + (match.surf_int_y-img.surf_int_y)**2 + (match.surf_int_z-img.surf_int_z)**2 )
        phase_diff = abs(img.phase_angle-match.phase_angle)
        alt_diff = abs(img.sc_altitude-match.sc_altitude)

        # if (dist < img.half_width/2.) and (alt_diff<5.) and (phase_diff<25.): # this option resulted in matches_phase_diff_25.csv
        if (dist < img.half_width/2.) and (alt_diff<5.) and (phase_diff<MAX_PHASE_DIFFERENCE):
            distance.append(dist)
            matches.append(idx)
            
    if len(matches)>0:
        return matches[distance.index(min(distance))], min(distance)
    else:
        return None, None


# Loop through all pre-perihelion images and find the best post-perihelion image, if any
# Note that this is not at all optimised, and running all the combinations is going to be slooow

match_pre = []
match_post = []
for idx1 in pre.index:
    idx2, dist = best_match(pre, post, idx1)
    if idx2 is None:
        continue
    else:
        match_pre.append(idx1)
        match_post.append(idx2)
        

# Save the pairs to a csv

match_df = pd.DataFrame({
    'match_pre': match_pre, 
    'pre_browse_url': map(lambda x: pre.loc[x].browse_url, match_pre),
    'pre_vec1': map(lambda x: pre.loc[x].vec1, match_pre),
    'pre_vec2': map(lambda x: pre.loc[x].vec2, match_pre),
    'pre_start_time': map(lambda x: pre.loc[x].start_time, match_pre),

    'match_post': match_post, 
    'post_browse_url': map(lambda x: post.loc[x].browse_url, match_post),
    'post_vec1': map(lambda x: post.loc[x].vec1, match_post),
    'post_vec2': map(lambda x: post.loc[x].vec2, match_post),
    'post_start_time': map(lambda x: post.loc[x].start_time, match_post)
})
match_df.to_csv(os.path.join('.', 'matches-F22-phase-angle-' + str(MAX_PHASE_DIFFERENCE) + '.csv'), index=False)


