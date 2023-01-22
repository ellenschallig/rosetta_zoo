# Needs osinac_metadata_orientation.csv.gz, get this from https://github.com/msbentley/osiris_zoo/blob/bffd2d7506a8297cf01011198cd2196eb658a69e/osinac_metadata.csv.gz

import urllib
import os
import pandas as pd

data_path = '.'

# Download all the OSIRIS images that are taken with the F22 (Orange) filter.

images = pd.read_csv(os.path.join(data_path, 'osinac_metadata_orientation.csv.gz'))
images = images[images.prod_id.str.contains('F22.FIT')]

def download_image(row):
    url = row.browse_url
    filename = "./downloaded_images/" + os.path.basename(url)
    if not os.path.exists(filename):
        urllib.request.urlretrieve(url, filename)

for idx, row in images.iterrows():
    print(idx)
    download_image(row)
