import os
import ee
import geemap

import csv

from datetime import datetime, timedelta

from PIL import Image, ImageOps
import shutil

END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=365)

END_DATE_STR = END_DATE.strftime("%Y-%m-%d")
START_DATE_STR = START_DATE.strftime("%Y-%m-%d")

OUT_DIR = os.path.expanduser('./downloads/')
RADIUS = 800

def getImgForAoi(aoi, imageCollectionAssetId, latest):

    if imageCollectionAssetId == 'USDA/NAIP/DOQQ':
        collection = (
            ee.ImageCollection(imageCollectionAssetId)
            .filterBounds(aoi.geometry())
            .filterDate("2019-01-01", "2023-01-01")
        )
        image = collection.limit(1, 'system:time_start', False).first()

    elif 'LANDSAT' in imageCollectionAssetId:
        if latest:
            collection = (
                ee.ImageCollection(imageCollectionAssetId)
                .filterBounds(aoi.geometry())
                .filterDate(START_DATE_STR, END_DATE_STR)
            )
            image = collection.limit(1, 'system:time_start', False).first()
        else:
            collection = (
                ee.ImageCollection(imageCollectionAssetId)
                .filterBounds(aoi.geometry())
                .filterDate(START_DATE_STR, END_DATE_STR)
                .sort("CLOUD_COVER")
                .limit(1)
            )
            image = collection.first()

    elif 'COPERNICUS' in imageCollectionAssetId:
        if latest:
            collection = (
                ee.ImageCollection(imageCollectionAssetId)
                .filterBounds(aoi.geometry())
                .filterDate(START_DATE_STR, END_DATE_STR)
            )
            image = collection.limit(1, 'system:time_start', False).first()
        else:
            collection = (
                ee.ImageCollection(imageCollectionAssetId)
                .filterBounds(aoi.geometry())
                .filterDate(START_DATE_STR, END_DATE_STR)
                .sort("CLOUDY_PIXEL_PERCENTAGE")
                .limit(1)
            )
            image = collection.first()
    return image.set({
        'aoi': aoi.geometry(),
        # 'name': name
    }).clip(aoi.geometry())


def latLongToBbox(feature):
    bbox = feature.geometry().buffer(RADIUS).bounds()
    # bbox = ee.Geometry.Point([80.968294, 26.85694]).buffer(RADIUS).bounds()

    return ee.Feature(bbox).copyProperties(feature).set({
                    'center': feature.geometry(),
                    # 'name': feature.get('name')
                    });

def generate_and_download_chips(roi, bands, dimensions, title, title_xy,
                                add_text, text_xy, imageCollectionAssetId,
                                latest=False, crs="epsg:4326"):

    def _map_helper(aoi):
        return getImgForAoi(aoi, imageCollectionAssetId, latest)

    ee.Initialize()

    bboxes = roi.map(latLongToBbox)

    images_collection = ee.ImageCollection(bboxes.map(_map_helper))

    # aois = []
    # bboxes = []
    # images = []
    # names_collection = ['1', '2']
    #
    # for l in range(2):
    #     # if l[0] == 'name':
    #     #     continue
    #
    #     # point_geom = ee.Geometry.Point([float(l[2]), float(l[1])])
    #     point_geom = ee.Geometry.Point([80.968294, 26.85694])
    #     aois.append(point_geom)
    #
    #     bbox = ee.Feature(point_geom.buffer(RADIUS).bounds())
    #     bboxes.append(bbox)
    #
    #     # image = getImgForAoi(bbox, l[0])
    #     image = getImgForAoi(bbox, f"""Lucknow_{l}""")
    #     images.append(image)
    #
    #     # names_collection.append(l[0])
    #     names_collection.append(f"""Lucknow_{l}""")
    #
    # aoi_collection = ee.FeatureCollection(aois)
    # bboxes_collection = ee.FeatureCollection(bboxes)
    # images_collection = ee.ImageCollection(images)

    if imageCollectionAssetId == 'USDA/NAIP/DOQQ':
        vis_params = {
            'bands': ['R', 'G', 'B'],
            'min': 0.0,
            'max': 255.0,
            'gamma': 1.4,
        }
    else:
        vis_params = {
            # 'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
            'bands': bands,
            'min': 0,
            'max': 6000,
            # 'max': 0.6*65455,
            'gamma': 1.4,
        }

    os.system("rm -rf ./downloads/*.jpg")

    geemap.get_image_collection_thumbnails(
        images_collection, OUT_DIR, vis_params, dimensions=500, format="jpg"
        # names = names_collection
    )

    shutil.make_archive('images', 'zip', OUT_DIR)

    for img_filename in filter(lambda file: ".jpg" in file, map(lambda f: os.path.join(OUT_DIR, f), os.listdir(OUT_DIR))):
        img = Image.open(img_filename)
        img_with_border = ImageOps.expand(img, border=10, fill='white')
        img_with_border.save(img_filename)

    return list(filter(lambda file: ".jpg" in file, map(lambda f: os.path.join(OUT_DIR, f), os.listdir(OUT_DIR))))
