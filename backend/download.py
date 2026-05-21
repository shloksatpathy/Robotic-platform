
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from ultralytics.utils import TQDM
from ultralytics.utils.checks import check_requirements
from ultralytics.utils.downloads import download
from ultralytics.utils.ops import xyxy2xywhn

check_requirements("faster-coco-eval")
from faster_coco_eval import COCO

# Train, Val Splits
dir = Path(yaml["path"])
for split, patches in [("train", 50 + 1), ("val", 43 + 1)]:
    print(f"Processing {split} in {patches} patches ...")
    images, labels = dir / "images" / split, dir / "labels" / split
    images.mkdir(parents=True, exist_ok=True)
    labels.mkdir(parents=True, exist_ok=True)

    # Download
    url = f"https://dorc.ks3-cn-beijing.ksyun.com/data-set/2020Objects365%E6%95%B0%E6%8D%AE%E9%9B%86/{split}/"
    if split == "train":
        download([f"{url}zhiyuan_objv2_{split}.tar.gz"], dir=dir)  # annotations json
        download([f"{url}patch{i}.tar.gz" for i in range(patches)], dir=images, threads=17)  # 51 patches / 17 threads = 3
    elif split == "val":
        download([f"{url}zhiyuan_objv2_{split}.json"], dir=dir)  # annotations json
        download([f"{url}images/v1/patch{i}.tar.gz" for i in range(15 + 1)], dir=images, threads=16)
        download([f"{url}images/v2/patch{i}.tar.gz" for i in range(16, patches)], dir=images, threads=16)

    # Move
    files = list(images.rglob("*.jpg"))
    with ThreadPoolExecutor(max_workers=16) as executor:
        list(TQDM(executor.map(lambda f: f.rename(images / f.name), files), total=len(files), desc=f"Moving {split} images"))

    # Labels
    coco = COCO(dir / f"zhiyuan_objv2_{split}.json")
    names = [x["name"] for x in coco.loadCats(coco.getCatIds())]
    for cid, cat in enumerate(names):
        catIds = coco.getCatIds(catNms=[cat])
        imgIds = coco.getImgIds(catIds=catIds)

        def process_annotation(im):
            """Process and write annotations for a single image."""
            try:
                width, height = im["width"], im["height"]
                path = Path(im["file_name"])
                with open(labels / path.with_suffix(".txt").name, "a", encoding="utf-8") as file:
                    annIds = coco.getAnnIds(imgIds=im["id"], catIds=catIds, iscrowd=None)
                    for a in coco.loadAnns(annIds):
                        x, y, w, h = a["bbox"]  # bounding box in xywh (xy top-left corner)
                        xyxy = np.array([x, y, x + w, y + h])[None]  # pixels(1,4)
                        x, y, w, h = xyxy2xywhn(xyxy, w=width, h=height, clip=True)[0]  # normalized and clipped
                        file.write(f"{cid} {x:.5f} {y:.5f} {w:.5f} {h:.5f}\n")
            except Exception as e:
                print(e)

        images_list = coco.loadImgs(imgIds)
        with ThreadPoolExecutor(max_workers=16) as executor:
            list(TQDM(executor.map(process_annotation, images_list), total=len(images_list), desc=f"Class {cid + 1}/{len(names)} {cat}"))