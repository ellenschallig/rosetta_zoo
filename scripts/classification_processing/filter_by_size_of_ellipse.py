DEFAULT_USER_RATIO = 0.8
DEFAULT_CLASSIFICATION_RATIO = 0.6

class FilterBySizeOfEllipse:
  def __init__(self, user_ratio = DEFAULT_USER_RATIO, classification_ratio = DEFAULT_CLASSIFICATION_RATIO):
    self.user_ratio = user_ratio
    self.classification_ratio = classification_ratio

  def filter(self, dataset):
    small_enough = dataset['small_enough'] == True
    high_user_ratio = dataset['user_ratio'] > self.user_ratio
    high_classification_ratio = dataset['classification_ratio'] > self.classification_ratio

    # Remove both single ellipses that are too large, as well as all ellipses from volunteers who
    # have drawn many large ellipses across all their classifications (deemed as "imprecise volunteers"), and single classifications that have too many large ellipses ("imprecise classifications")
    return dataset[small_enough & high_user_ratio & high_classification_ratio]
