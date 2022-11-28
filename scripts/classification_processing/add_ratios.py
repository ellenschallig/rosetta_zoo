class AddRatios:
  def __init__(self):
    pass

  def add_ratios(self, dataset):
    dataset = self.add_user_ratio_column(dataset)
    dataset = self.add_classification_ratio_column(dataset)
    return dataset

  def add_user_ratio_column(self, dataset):
    # ratio is number of small ellipses over the total number of ellipses made by a user, over all of their classifications
    # 'small enough' ellipse is defined in tag_large_ellipses.py 
    grouped_by_user = dataset.groupby('user_name')

    for user_name, rows_for_user in grouped_by_user:
      total_number_of_ellipses = rows_for_user.shape[0]
      number_of_small_enough_ellipses = rows_for_user[rows_for_user["small_enough"] == True].shape[0]
      
      ratio = number_of_small_enough_ellipses / total_number_of_ellipses
      dataset.loc[dataset['user_name'] == user_name, 'user_ratio'] = ratio

    return dataset

  def add_classification_ratio_column(self, dataset):
    # ratio is number of small ellipses over total number of ellipses in one classification
    # 'small enough' is defined in tag_large_ellipses.py
    grouped_by_ids = dataset.groupby('classification_id')

    for classification_id, rows_for_classification in grouped_by_ids:
      total_number_of_ellipses = rows_for_classification.shape[0]
      number_of_small_enough_ellipses = rows_for_classification[rows_for_classification["small_enough"] == True].shape[0]

      ratio = number_of_small_enough_ellipses / total_number_of_ellipses
      dataset.loc[dataset['classification_id'] == classification_id, 'classification_ratio'] = ratio
    
    return dataset
