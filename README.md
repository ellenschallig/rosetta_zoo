# Rosetta Zoo documentation

## Goal of the project
Use the OSIRIS NAC images from the Rosetta mission to map out changes on comet 67P/Churyumov-Gerasimenko over the duration of the mission. Do this on the Zooniverse platform, with the help from volunteers from all over the world. Deliver the data in a format that can be used by researchers.


## Subject preparation


### Make the image pairs

The text below loosely describes the process coded in https://github.com/msbentley/osiris_zoo, with some additions and changes not in that repository; those files (generate_pairs.py, generate_subjects.py & download_images.py) are in the https://github.com/ellenschallig/rosetta_zoo repository.

#### rosetta_zoo_getlabels.ipynb & rosetta_zoo_metadata.ipynb & rosetta_zoo_orientation.ipynb
The Planetary Science Archive (PSA) holds all the images from the Rosetta mission. These images are included multiple times, with different processing levels. For our purposes, we are only interested in the OSIRIS NAC images, with PSA processing level 3. The output of this ipython notebook lives in https://github.com/msbentley/osiris_zoo/tree/main/labels and is only an intermediate product.

Instead of looking at the full images each time, construct a dataframe with just the metadata, and save it to a csv. This file lives in https://github.com/msbentley/osiris_zoo/blob/main/osinac_metadata.csv.gz, and again is an intermediate product.

For each image in the set, calculate the vector between the midpoint of the image and the comet's north, to be able to draw an arrow on the image to comet north later. Save the updated dataframe to another csv. This lives here: https://github.com/msbentley/osiris_zoo/blob/bffd2d7506a8297cf01011198cd2196eb658a69e/osinac_metadata_orientation.csv.gz, so you don't have to run the notebook itself (which is impossible because of dependencies that are not online). This is the important file to be able to run the code described below.

#### rosetta_zoo_pairs.ipynb & generate_pairs.py
generate_pairs.py is adapted from rosetta_zoo_pairs.ipynb

To map any changes, we have to compare images with enough detail to see small-scale changes. To this end, we selected images from closer than 50 km from the surface of the comet (done in rosetta_zoo_metadata.ipynb). We also selected the images taken in the F22 (orange) filter, to avoid the almost duplicates taken in the other filters (only a few seconds apart, therefore almost exactly the same image as the F22 image).
This left us with about 4100 images.

To be able to compare images in time, we have to decide how to select the images to be compared. We chose perihelion ('2015-08-13T02:03:00Z') as the cut-off point to divide the set into two subsets.* The pre-perihelion subset contained about 1100 images, the post-perihelion set about 3000.

For each image in the pre-perihelion set, find the one in the post-perihelion set that best matches it in terms of overlapping area (the 'boresight intercept' and field of view) and phase angle. The distance between the boresight intercepts must be smaller than half the image width, the altitude difference less than 5 degrees and the phase angle difference less than 25 degrees. Then from all the images in the post-perihelion set pick the one that has the smallest overall difference. These values were proposed as a sensible start and could be changed to optimise the pair selection, but ultimately were deemed to be good enough for this first set of pairs. Anything that was not a useful pairing would be quickly flagged by the volunteers. This left us with 925 pairs.

* This is a good start, but by no means the only way to make 'before' and 'after' subsets. One could choose other cut-off dates, or even have a rolling cut off, so images taken about six weeks apart (for example) are compared with each other. This last choice would be particularly useful in certain areas that changed a lot over time (but alas we had no time for it during this project).

### Make the images ready for the Zooniverse platform 

#### download_images.py

Download all the images (JPG format, processed by the PSA team) from those 925 pairs; 1395 unique images. Several images from the post-perihelion set are used multiple times. Or just download all of the images (like in download_images.py) that could be used for this exercise in case you want to make other comparisons later.

#### generate_subjects.py

To give the volunteers an idea of how to orient the images in each pair with respect to each other, draw an arrow to the comet north on each image. This is useful for many pairs, but because it's only a 2-dimensional representation of the oddly shaped 3-dimensional object, you may get strange pointings in a few pairs. (Also when you get close to a pole the arrows can be less than helpful.) This was done with code based on rosetta_zoo_orientation.ipynb.

Do note that in the end we did not rotate the images ourselves before uploading them to the Zooniverse platform (so that bit of the code in rosetta_zoo_pairs.ipynb can be ignored), but the Zooniverse Team added free rotation functionality to our project. Therefore the volunteers could orient the images however they wanted.

Make a manifest.csv that contains all the pairs, with extra metadata. Compress the images that are >1 MB to <1 MB (Zooniverse restrictions) (not in any file, I did this by hand). Then upload all this to the platform.

### Weed out the unusable images

The above set still contains images that are too dark (such as photos taken from the side of the comet away from the sun) or something has gone wrong during the imaging. The volunteers have the option to classify these pairs as 'too dark/otherwise unusable'. After a few weeks we selected the pairs that had 3 or more of those classifications, checked each of them to find which image in the pair was not usable, and then retired each pair that included those images. 291 pairs were retired this way. All the other pairs went through 40 classifications before being retired automatically.


## Data reduction after classifications

A pipeline (run_classification_processing.py) processes the raw data into several products.

Some Zooniverse terminology:
Each set of ellipses drawn by a single user for a single pair of images is called a 'classification'.
Each ellipse itself is called a 'mark'.
frame: each image in the pair. frame = 0 is the before or first image, frame = 1 is the after or second image


#### read_classifications.py
The raw classifications are downloaded from the project page on Zooniverse, which provides it in csv format. Unnecessary columns are removed. The workflow number with which the project was launched (in this case "79.165") is used to filter the project data from earlier tries. This is returned as a pandas dataframe.
The current classification file is "rosetta-zoo-classifications-6.csv", which includes all the classifications up to 22 Nov 2022.

#### extract_ellipses.py
The classifications dataframe is processed to extract all ellipses drawn onto each pair of images. Each set of ellipses drawn by a single user for a single pair of images is called a 'classification'. An 'annotation' is an answer to one of the tasks in the workflow, and for task T0 this can include zero, one, or multiple ellipses. Task T1 ('Did you look for changes all over the images') is removed from the dataset at this point. Each ellipse ends up on a separate row, with each parameter/attribute split into separate columns. This is then returned as another pandas dataframe.

#### tag_large_ellipses.py
This step introduces a new column 'small_enough' for filtering later on. If an ellipse is deemed to be too large, controlled by DEFAULT_MAX_SIZE (currently 1/9 of the area of a full image), then this ellipse should be excluded from further consideration. The column will then say False.
This is included because some ellipses are purely drawn and submitted by volunteers for fun, not because there is really something there. From a certain size we can be sure that an ellipse is just too large to be in any way useful. The area chosen (1/9 of a full image) is conservative in that there remain probably still a lot of ellipses that are not useful, but are smaller than this threshold.
The DEFAULT_MAX_SIZE can be changed to a different value (and maybe even should be, depending on use case).

#### add_ratios.py
Two columns are added which depend on the 'small_enough' column from the previous step.
Take into account that only logged in volunteers consistently keep the same username from classification to classification. Volunteers that are not logged in get a username based on (a hashed form of) the ip-address, so this can change from session to session, or different users can have the same username (if a computer is shared).
For each username calculate two things:
	0.	Take all the ellipses drawn by this user over all their classifications, find how many are small enough and calculate the ratio. Add this number to the column 'user_ratio'.
	0.	Take all the ellipses drawn in a single classification (so for one pair of images) and calculate the ratio of useable ellipses. Add this to the column 'classification_ratio'.

#### filter_by_size_of_ellipse.py
Now filter out the ellipses, classifications and users that do not satisfy the given threshold values in DEFAULT_USER_RATIO (0.8) and DEFAULT_CLASSIFICATION_RATIO (0.6). Again these values are probably quite conservative and can be changed.

#### calculate_pixels.py
Now for each pair of images (each unique subject_id) make a list of all the pixels that are included in the ellipses. If different volunteers mark the same area, add a count to the pixel. If a volunteer overlaps some area with ellipses, and with different reasons (or no reason), also add a count to those pixels. However if the reason is the same (for example a boulder that appeared twice) then do not add a count. The counts are added per colour of ellipse that was used (or 'tool' in the code), where yellow = appeared, blue = moved and red = disappeared. Of course this is done for each image in the pair separately (or 'frame' in the code).
If more information on the change is given by the volunteer, then this is included in the later columns.

Each pair of images, with a unique subject_id, then returns a list of pixels that have at least a single count, for both images in the pair. Each file is formatted as a csv and can have at most 2x 2048x2048 rows, each row is a pixel.