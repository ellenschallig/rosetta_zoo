import ipdb
import csv

from classification_processing.read_classifications import ReadClassifications
from classification_processing.extract_ellipses_from_classifications import ExtractEllipses
from classification_processing.tag_large_ellipses import TagLargeEllipses
from classification_processing.add_ratios import AddRatios
from classification_processing.filter_by_size_of_ellipse import FilterBySizeOfEllipse
from classification_processing.calculate_pixels import CalculatePixels, CSV_FIELD_NAMES

classifications = ReadClassifications().run()

# classifications = classifications[classifications['subject_id'] == 75637391]

ellipses = ExtractEllipses().extract(classifications)
tagged = TagLargeEllipses().tag(ellipses)
ratioed = AddRatios().add_ratios(tagged)
filtered = FilterBySizeOfEllipse().filter(ratioed)
filtered.to_csv('filtered.csv', index=False)

print(ellipses)

def calculate_and_write_csv(subject_id, group):
  print(subject_id)
  pixels = CalculatePixels().calculate(group)

  # Use csv here, because pandas gets slow for this large amount of rows
  with open("pixels-%s.csv" % str(subject_id), 'w') as csvfile:
    print("writing csv")
    writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELD_NAMES)
    writer.writeheader()
    writer.writerows(pixels)

[calculate_and_write_csv(subject_id, group) for subject_id, group in filtered.groupby('subject_id')]