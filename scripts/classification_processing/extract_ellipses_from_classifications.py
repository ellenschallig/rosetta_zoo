import pandas as pd
import numpy as np
import json

class ExtractEllipses:
  def __init__(self):
    pass

  def extract(self, classifications: pd.DataFrame):
    dataset = classifications.copy()

    # Convert JSON into Python Dict
    dataset['annotations'] = dataset["annotations"].transform(lambda x: json.loads(x))

    # Convert list of annotations into one row for each item in list
    dataset = dataset.explode('annotations')
    dataset.rename(columns={"annotations": "annotation"}, inplace=True)

    dataset["task"] = dataset["annotation"].transform(lambda annotation: annotation['task'])
    dataset["task_value"] = dataset["annotation"].transform(lambda annotation: annotation['value'])
    dataset.drop(['annotation'], axis=1, inplace=True)

    # Remove T1 tasks
    dataset = dataset[dataset["task"] == "T0"]

    # Convert each mark into row
    dataset = dataset[dataset["task_value"].transform(lambda value: len(value)) > 0] # Remove classifications without marks
    dataset = dataset.explode('task_value')

    # Convert task_value into columns
    dataset['x'] = dataset['task_value'].transform(lambda value: value['x'])
    dataset['y'] = dataset['task_value'].transform(lambda value: value['y'])
    dataset['rx'] = dataset['task_value'].transform(lambda value: value['rx'])
    dataset['ry'] = dataset['task_value'].transform(lambda value: value['ry'])
    dataset['angle'] = dataset['task_value'].transform(lambda value: value['angle'])
    dataset['frame'] = dataset['task_value'].transform(lambda value: value['frame'])
    dataset['tool'] = dataset['task_value'].transform(lambda value: value['tool'])
    dataset['detail_number'] = dataset['task_value'].transform(self.get_detail_number).replace({np.nan: None})
    dataset.drop(["task_value"], axis=1, inplace=True) # Remove Dict column "task_value", all data is now individual columns

    rx_exists = dataset['rx'] > 0
    ry_exists = dataset['ry'] > 0
    dataset = dataset[rx_exists & ry_exists] # Remove ellipses that were left in by volunteers who made the radius zero but didn't remove them

    return dataset

  def get_detail_number(self, mark):
    """
      moved_labels = ["Boulder", "Dust transport", "Scarp migration", "Something else", "Don't know"]
      disappeared_labels = ["Pit", "Boulder", "Cliff", "Dust", "Escarpment", "Something else", "Don't know"]
      appeared_labels = ["Pit", "Boulder", "Cliff collapse", "Dust", "Something else", "Don't know"]
      'tool' = {0,1,2} is moved, disappeared, appeared

      This results in eg 000 = Boulder, 100 = Pit, 101 = Boulder, 204 = Something Else
      This annoying list because not all flags are the same for each 'tool'
    """
    chosen_detail_option = mark['details'][0]['value']

    if chosen_detail_option:
      detail_number = int(mark['tool']*100 + chosen_detail_option)
    else:
      detail_number = None

    return detail_number
