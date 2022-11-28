import numpy as np

DEFAULT_MAX_SIZE = (1./9) * (2048*2048) # max size of ellipse, fraction of full image

class TagLargeEllipses:
  def __init__(self, max_size = DEFAULT_MAX_SIZE):
    self.max_size = max_size

  def tag(self, dataset):
    sizes = np.pi * dataset['rx'] * dataset['ry']
    small_enough = sizes < self.max_size
    dataset["small_enough"] = small_enough

    return dataset
