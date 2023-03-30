#!/usr/bin/env python3
import os
import json
from tqdm import tqdm
from pathlib import Path
from PIL import Image

json_files = os.listdir('json_crops')
image_dirs = list(map(lambda x: x.split('::')[0], json_files))
print(image_dirs)

for i, json_file in enumerate(json_files):
    dirname = json_file.split('::')[0]
    #images_dir = Path('images') / dirname
    print("=================================================================")
    print(f"=========== Processing {dirname}  :: {i+1}/{len(json_files)} ============")
    print("=================================================================")

    with open(Path('json_crops') / json_file, 'r') as jfp:
        js = json.load(jfp)

    # Change to new format and discard thresholds
    converted = dict()

    for entry in js['images']:
        key = entry['file']
        obj = list()

        for detection in entry['detections']:
            if int(detection['category']) != 1:
                continue
            elif detection['conf'] < 0.1:
                continue
            else:
                obj.append(detection)

        if len(obj) > 0:  # Discard no-detection ones
            converted[key] = obj

    for path, detections in tqdm(converted.items()):
        path = Path(path)
        path = Path('images') / dirname / path.name
        out = Path('detected') / dirname / path.name

        image = Image.open(path)

        rw, rh = image.size
        x, y, w, h = detections[0]['bbox']

        left = x * rw
        upper = y * rh
        right = left + w * rw
        lower = upper + h * rh

        image = image.crop((left, upper, right, lower))
        image.save(out)

exit(1)

#print(os.listdir('json_crops'))


print(js['detection_categories'])


# {
#   file: str = path_to_image,
#   max_detection_conf: float,
#   detections: List[{category: int, conf: float, bbox: List[4]}]
# }




# Converted done here. Example:
# {
#     "/images/KinnardA_Nov16.100RECNX.IMG_0470.JPG": [
#         {
#             "category": "1",
#             "conf": 0.939,
#             "bbox": [
#                 0.6694,
#                 0.468,
#                 0.2392,
#                 0.1536
#             ]
#         }
#     ]
# }

image_paths = os.listdir('images')
filtered = {k:v for k,v in converted.items() if Path(k).name in image_paths}

for path, detections in filtered.items():
    path = Path(path)
    path = Path('images') / path.name
    out = Path('detected') / path.name

    image = Image.open(path)

    rw, rh = image.size
    x, y, w, h = detections[0]['bbox']

    left = x * rw
    upper = y * rh
    right = left + w * rw
    lower = upper + h * rh

    image = image.crop((left, upper, right, lower))
    image.save(out)

    #print(image.size, detections[0]['bbox'])

#print(json.dumps(converted, indent=4))
