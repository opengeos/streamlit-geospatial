import os
import ee
import geemap

import csv

OUT_DIR = os.path.expanduser('.')
RADIUS = 6000
VIS_PARAMS = {
    'bands': ['B6', 'B5', 'B4'],
    'min': 0,
    'max': 6000,
    'gamma': 1.4,
}

def getImgForAoi(aoi):
    collection = (
        ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
        .filterBounds(aoi.geometry())
        .sort("CLOUD_COVER")
        .limit(1)
    )

    image = collection.first()

    return image.set({
        'aoi': aoi.geometry(),
        # 'name': name
    }).clip(aoi.geometry())


def latLongToBbox(feature):
    bbox = feature.geometry().buffer(RADIUS).bounds()

    return ee.Feature(bbox).copyProperties(feature).set({
                    'center': feature.geometry(),
                    # 'name': feature.get('name')
                    });

def generate_and_download_chips(
    roi, out_gif, start_year, end_year, start_date, end_date, bands,
    apply_fmask, frames_per_second, dimensions, overlay_data, overlay_color,
    overlay_width, overlay_opacity, frequency, date_format, title, title_xy,
    add_text, text_xy, text_sequence, font_type, font_size, font_color,
    add_progress_bar, progress_bar_color, progress_bar_height, loop, mp4,
    fading):

    ee.Initialize()

    bboxes = roi.map(latLongToBbox)

    images_collection = ee.ImageCollection(bboxes.map(getImgForAoi))

    # aois = []
    # bboxes = []
    # images = []
    names_collection = ['1', '2']
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

    geemap.get_image_collection_thumbnails(
        images_collection, OUT_DIR, VIS_PARAMS, dimensions=500, format="jpg",
        names = names_collection
    )
    print("5")
