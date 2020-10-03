import os
import io
import os
import tqdm
import pandas as pd
import numpy as np
from google.cloud import vision
from PIL import Image
from google.cloud import vision
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error as MSE
import dask.array as da


features_g_df = pd.read_csv("/resource/FeatureTable_GoogleAnnot.PCA.csv", index_col=0)
meta = pd.read_csv("/resource/metadata.csv", index_col=0)
client = vision.ImageAnnotatorClient()
os.chdir("/resource/img/")

def get_nearest(fn):
    # TODO: adding try/except for flask
    out = {
        'distance_1': get_nearest_use_distance_1(fn),
        'distance_2': get_nearest_use_distance_2(fn),
        'distance_3': get_nearest_use_distance_3(fn),
        'distance_4': get_nearest_use_distance_4(fn),
    }
    return out

def get_metadata(fn):
    record = meta.loc[fn].to_dict()
    return record
'''
Distance 1: Cosine distance on GVision features
'''
def get_nearest_use_distance_1(fn):
    y = df_selected_PCs.loc[fn].values.reshape(1, -1)
    best_score = 1e10
    best_match = "No match found"
    for fn_iter in df_selected_PCs.index:
        if fn_iter != fn:
            x = df_selected_PCs.loc[fn].values.reshape(1, -1)
            score = 1 - cosine_similarity(y, x)
            if best_score > score:
                best_match = fn_iter
    return {best_match: best_score}

def get_google_feature(fn):
    feature = features_g_df.loc[record]
    return feature

def cosine_distance_GVision_PCA(fn1, fn2):
    x1 = df_selected_PCs.loc[fn1].values.reshape(1, -1)
    x2 = df_selected_PCs.loc[fn2].values.reshape(1, -1)
    dist = 1 - cosine_similarity(x1, x2)
    print("Cosine distance on GVision features for {}, {} = {}".format(fn1, fn2, dist))
    return dist


'''
Distance 2: Color distance in RGB space
'''
def get_nearest_use_distance_2(fn):
    y = get_dominant_color(fn)
    best_score = 1e10
    best_match = "No match found"
    for fn_iter in df_selected_PCs.index:
        if fn_iter != fn:
            x = get_dominant_color(fn_iter)
            score = color_distance(y, x)
            if best_score > score:
                best_match = fn_iter
    return {best_match: best_score}


def get_dominant_color(fn):
    with io.open(fn, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.image_properties(image=image)
    colors = response.image_properties_annotation.dominant_colors.colors
    return [(color.pixel_fraction, color.color.red, color.color.green, color.color.blue)
            for color in colors]


def color_distance(colors1, colors2):
    dist = 0
    for c1, c2 in zip(colors1, colors2):
        dR, dG, dB = c1[1]-c2[1], c1[2]-c2[2], c1[3]-c2[3]
        fraction_weight = c1[0]*c2[0]
        r_mean = (c1[1] + c2[1]) / 2
        dcolor = np.sqrt((2+r_mean/256)*dR**2 + 4*dG**2 + (3-r_mean/256)*dB**2)
        dist += fraction_weight * dcolor
    print("Color distance for {}, {} = {}".format(fn1, fn2, dist))
    return dist


'''
Distance 3: Cosine distance on rawdata (center cropping)
'''

def get_nearest_use_distance_3(fn):
    y = get_pic_array(fn)
    best_score = 1e10
    best_match = "No match found"
    for fn_iter in df_selected_PCs.index:
        if fn_iter != fn:
            x = get_pic_array(fn_iter)
            score = cosine_distance_raw_center_crop(y, x)
            if best_score > score:
                best_match = fn_iter
    return {best_match: best_score}


def crop_to_square(pic_array1, pic_array2):
    a1, b1 = pic_array1.shape[0: 2]
    a2, b2 = pic_array2.shape[0: 2]
    c = min(a1, b1, a2, b2)/2
    c1 = pic_array1[int(a1/2 - c):int(a1/2 + c), int(b1/2 - c):int(b1/2 + c)]
    c2 = pic_array2[int(a2/2 - c):int(a2/2 + c), int(b2/2 - c):int(b2/2 + c)]
    return c1, c2


def get_pic_array(img_filename):
    with Image.open(img_filename) as im:
        pic = np.array(im.getdata()).reshape(im.size[0], im.size[1], 3)
    return pic


def cosine_distance_raw_center_crop(pic1, pic2):
    x1, x2 = crop_to_square(pic1, pic2)
    dist = 1 - np.mean([cosine_similarity(x1[:,:,layer], x2[:,:,layer]) for layer in range(3)])
    print("Cosine distance on rawdata (center crop) for {}, {} = {}".format(fn1, fn2, dist))
    return dist

'''
Distance 4: Cosine distance on rawdata (center cropping)
'''
def get_nearest_use_distance_4(fn):
    y = get_pic_array(fn)
    best_score = 1e10
    best_match = "No match found"
    for fn_iter in df_selected_PCs.index:
        if fn_iter != fn:
            x = get_pic_array(fn_iter)
            score = euclidean_distance_raw_center_crop(y, x)
            if best_score > score:
                best_match = fn_iter
    return {best_match: best_score}


def euclidean_distance_raw_center_crop(fn1, fn2):
    pic1 = get_pic_array(fn1)
    pic2 = get_pic_array(fn2)
    x1, x2 = crop_to_square(pic1, pic2)
    dist = np.mean([MSE(x1[:,:,layer], x2[:,:,layer], squared=False) for layer in range(3)])
    print("Euclidean distance on rawdata (center crop) for {}, {} = {}".format(fn1, fn2, dist))
    return dist
