#!/usr/bin/env python3
import os
import json
from tqdm import tqdm
from pathlib import Path
from PIL import Image


class Point:
    def __init__(self, w, h):
        self.w = w
        self.h = w

    def __contains__(self, other):
        return other.w <= self.w and other.h <= self.h

    def __sub__(self, other):
        return Point(self.w - other.w, self.h - other.h)

    def max(self):
        return self.w if self.w > self.h else self.h

    def min(self):
        return self.w if self.w < self.h else self.h

    def __str__(self):
        return f"Point(w={self.w}, h={self.h})"


def get_points(rw, rh, x, y, w, h):
    p1 = Point(x * rw, y * rh)
    p2 = Point(p1.w + w * rw, p1.h + h * rh)

    max_p = Point(rw, rh)
    p2 = Point(p2.max(), p2.max())

    # Use a square crop that fits right away
    if p2 in max_p:
        return p1, p2

    # Move p1 and p2 diagonally back, as long as p1 stays positive
    needed_diag = (p2 - max_p).max()

    if needed_diag.max() == needed_diag.w:
        d_off = min(p1.w, needed_diag.w)
    else:
        d_off = min(p1.h, needed_diag.h)

    diag_off = Point(d_off, d_off)

    p1 -= diag_off
    p2 -= diag_off

    if p2 in max_p:
        return p1, p2

    # Move p1 and p2 in the maximal direction, until p1 is (0,0)
    needed_diag = (p2 - max_p).max()

    if p1.max() == p1.w and needed_diag.w > 0:
        max_offw = min(p1.max(), needed_diag.w)
        max_off = Point(max_offw, 0)
    elif p1.max() == p1.h and needed_diag.h > 0:
        max_offh = min(p1.max(), needed_diag.h)
        max_off = Point(0, max_offh)
    else:
        max_off = Point(0, 0)

    p1 -= max_off
    p2 -= max_off

    if p2 in max_p:
        return p1, p2

    # At this point p1 == (0,0)
    distance_remaining = (p2 - max_p).max()

    if distance_remaning > p2.min():
        raise OSError("Box crop is impossible")
    else:
        p2 -= Point(distance_remaining, distance_remaining)
        return p1, p2


json_files = os.listdir("json_crops")
image_dirs = list(map(lambda x: x.split("::")[0], json_files))
print(image_dirs)

for i, json_file in enumerate(json_files):
    dirname = json_file.split("::")[0]
    # images_dir = Path('images') / dirname
    print("=================================================================")
    print(f"=========== Processing {dirname}  :: {i+1}/{len(json_files)} ============")
    print("=================================================================")

    with open(Path("json_crops") / json_file, "r") as jfp:
        js = json.load(jfp)

    # Change to new format and discard thresholds
    converted = dict()

    for entry in js["images"]:
        key = entry["file"]
        obj = list()

        for detection in entry["detections"]:
            if int(detection["category"]) != 1:
                continue
            elif detection["conf"] < 0.1:
                continue
            else:
                obj.append(detection)

        if len(obj) > 0:  # Discard no-detection ones
            converted[key] = obj

    exeception_count = 0

    for path, detections in tqdm(converted.items()):
        path = Path(path)
        path = Path("images") / dirname / path.name
        out = Path("detected_boxed") / dirname / path.name

        image = Image.open(path)

        rw, rh = image.size
        x, y, w, h = detections[0]["bbox"]

        try:
            p1, p2 = get_points(rw, rh, x, y, w, h)
        except OSError:
            exeception_count += 1
            continue

        image = image.crop((p1.w, p1.h, p2.w, p2.h))
        image.save(out)

    print(f"{exeception_count} exceptions in {dirname}")

exit(1)

# print(os.listdir('json_crops'))


print(js["detection_categories"])


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

image_paths = os.listdir("images")
filtered = {k: v for k, v in converted.items() if Path(k).name in image_paths}

for path, detections in filtered.items():
    path = Path(path)
    path = Path("images") / path.name
    out = Path("detected") / path.name

    image = Image.open(path)

    rw, rh = image.size

    x, y, w, h = detections[0]["bbox"]

    try:
        p1, p2 = get_points(rw, rh, x, y, w, h)
    except:
        continue

    image = image.crop((p1.w, p1.h, p2.w, p2.h))
    image.save(out)
