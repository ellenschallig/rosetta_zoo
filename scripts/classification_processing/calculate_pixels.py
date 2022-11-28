from itertools import groupby
from json import tool
from math import nan
import numpy as np
import ipdb

# # F = sqrt(rx^2, ry^2)
# # F: distance of Focus Point to Center
# # rx = radius of major axis
# # ry = radius of minor axis
# def foci(rx, ry):

DEG_TO_RAD = np.pi / 180
TOOL_TO_CSV_COLUMN = {
  0: "moved",
  1: "disappeared",
  2: "appeared"
}

DETAIL_NUMBER_TO_CSV_COLUMN = {
  0: "moved_boulder",
  1: "moved_dust_transport",
  2: "moved_scarp_migration",
  3: "moved_something_else",
  4: "moved_dont_know",
  100: "disappeared_pit",
  101: "disappeared_boulder",
  102: "disappeared_cliff",
  103: "disappeared_dust",
  104: "disappeared_escarpment",
  105: "disappeared_something_else",
  106: "disappeared_dont_know",
  200: "appeared_pit",
  201: "appeared_boulder",
  202: "appeared_cliff_collapse",
  203: "appeared_dust",
  204: "appeared_something_else",
  205: "appeared_dont_know"
}

CSV_FIELD_NAMES = ["frame", "x", "y"] + list(TOOL_TO_CSV_COLUMN.values()) + list(DETAIL_NUMBER_TO_CSV_COLUMN.values())

class Ellipse:
  def __init__(self, row):
    self.row = row

    angle_radians = row["angle"] * DEG_TO_RAD
    self.angle_cos = np.cos(angle_radians)
    self.angle_sin = np.sin(angle_radians)

    # note: image size here hardcoded as 2048 x 2048
    max_radius = np.max([row["rx"], row["ry"]])
    self.bound_left   = max(0, row["x"] - max_radius)
    self.bound_right  = min(row["x"] + max_radius, 2047)
    self.bound_top    = max(0, row["y"] - max_radius)
    self.bound_bottom = min(row["y"] + max_radius, 2047)

    self.center_x = row["x"]
    self.center_y = row["y"]
    self.rx = row["rx"]
    self.ry = row["ry"]

  def pixels(self):
    # For every pixel in de square bounding box for this ellipse
    for x in range(int(np.floor(self.bound_left)), int(np.ceil(self.bound_right)) + 1):
      for y in range(int(np.floor(self.bound_top)), int(np.ceil(self.bound_bottom)) + 1):
        # If it's actually inside the ellipse
        if self.includes(x, y):
          # Then yield this pixel to the for loop that called this method
          yield (x,y)

  def includes(self, x, y):
    dx = x - self.center_x
    dy = y - self.center_y
    tdx = self.angle_cos * dx - self.angle_sin * dy
    tdy = self.angle_sin * dx + self.angle_cos * dy

    return (((tdx**2) / (self.rx**2)) + ((tdy**2) / (self.ry**2))) <= 1

class CalculatePixels:
  def __init__(self):
    pass

  def calculate(self, dataset):
    retval = []

    for frame in [0, 1]:
      ellipses = [Ellipse(row) for idx, row in dataset[dataset["frame"] == frame].iterrows()]
      pixels = dict()

      for ellipse in ellipses:
        for pixel in ellipse.pixels():
          if (pixel in pixels.keys()):
            # print("SKIP", pixel)
            pass # Already processed this from another ellipse
          else:
            x, y = pixel
            matching_ellipses_for_pixel = filter(lambda el: el.includes(x, y), ellipses)
            pixels[pixel] = self.aggregate(frame, x, y, matching_ellipses_for_pixel)

      retval.extend(pixels.values())

    return retval

  def aggregate(self, frame, x, y, ellipses):
    aggregated = {
      "frame": frame,
      "x": x,
      "y": y,
      "moved": 0,
      "disappeared": 0,
      "appeared": 0,
      "moved_boulder": 0,
      "moved_dust_transport": 0,
      "moved_scarp_migration": 0,
      "moved_something_else": 0,
      "moved_dont_know": 0,
      "disappeared_pit": 0,
      "disappeared_boulder": 0,
      "disappeared_cliff": 0,
      "disappeared_dust": 0,
      "disappeared_escarpment": 0,
      "disappeared_something_else": 0,
      "disappeared_dont_know": 0,
      "appeared_pit": 0,
      "appeared_boulder": 0,
      "appeared_cliff_collapse": 0,
      "appeared_dust": 0,
      "appeared_something_else": 0,
      "appeared_dont_know": 0
    }

    # Remove ellipses when they are from the same classification and for the same type
    # Eg if one classification has two overlapping ellipses both for boulder (2 adjacent boulders have been marked)
    # then the overlapping pixels shouldn't claim to be two votes for a boulder, otherwise the space
    # between boulders would be "more certain" to be a boulder than the centers of the ellipses.

    ellipses = unique_by(ellipses, lambda ellipse: "%s-%s" % (ellipse.row["classification_id"], ellipse.row["detail_number"]))

    for ellipse in ellipses:
      tool_column = TOOL_TO_CSV_COLUMN[ellipse.row["tool"]]
      aggregated[tool_column] += 1

      if ellipse.row["detail_number"]:
        tool_and_detail_column = DETAIL_NUMBER_TO_CSV_COLUMN[ellipse.row["detail_number"]]
        aggregated[tool_and_detail_column] += 1

    return aggregated

def unique_by(iterable, keying_function):
   
  seen_keys = set()
  output = []

  for element in iterable:
    element_key = keying_function(element)

    if not element_key in seen_keys:
      seen_keys.add(element_key)
      output.append(element)
  return output