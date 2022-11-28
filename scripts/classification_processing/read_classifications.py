import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(__file__)
DEFAULT_STORAGE_PATH = os.path.join(SCRIPT_DIR, "../../classification_data")
DEFAULT_CLASSIFICATION_FILENAME = os.path.join(DEFAULT_STORAGE_PATH, "rosetta-zoo-classifications-5.csv")

class ReadClassifications:
  def __init__(self, path = DEFAULT_CLASSIFICATION_FILENAME, workflow_version = "79.165"):
    self.path = path
    self.workflow_version = workflow_version

  def run(self):
    all_classifications = pd.read_csv(self.path, dtype={"workflow_version": "string"})

    # Remove unwanted columns
    all_classifications.drop(['user_id', 'user_ip', 'created_at', 'workflow_name', 'workflow_id', 'subject_data', 'gold_standard', 'expert', 'metadata'], axis=1, inplace=True)

    # Rename subject_ids column since this project uses only 1 subject per classification
    all_classifications.rename(columns={'subject_ids': "subject_id"}, inplace=True)

    # Filter to specified workflow version
    for_workflow_version = all_classifications[all_classifications['workflow_version'] == self.workflow_version]
    for_workflow_version.drop(['workflow_version'], axis=1, inplace=True)

    return for_workflow_version

