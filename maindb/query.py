import os
import io
import os
import pandas as pd
import numpy as np
from google.cloud import vision
from PIL import Image
from google.cloud import vision
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error as MSE
import pickle as pkl
import time
import tqdm


features_g_df = pd.read_csv("/resource/FeatureTable_GoogleAnnot.PCA.csv", index_col=0)
pooling_df = pd.read_csv("/resource/FeatureTable_Pooling.csv", index_col=0)
color_pkl = pkl.load(open("/resource/FeatureTable_DominantColors.pkl", 'rb'))
meta = pd.read_csv("/resource/metadata.csv", index_col=0)
client = vision.ImageAnnotatorClient()
path = "resource/img"  # on master node
path = "/resource/img/"

def get_nearest(fn):
    # TODO: adding try/except for flask
    if True:  # TODO: pass a boole for filename/file
        fns = os.listdir(path)
        out = {
            'distance_1': get_nearest_use_distance_1_fn(fn, fns),
            'distance_2': get_nearest_use_distance_2_fn(fn, fns),
            'distance_3': get_nearest_use_distance_3_fn(fn, fns),
            'distance_4': get_nearest_use_distance_4_fn(fn, fns)
        }
    return out

def get_metadata(fn):
    record = meta.loc[fn].to_dict()
    return record
'''
Distance 1: Cosine distance on GVision features
'''
def get_nearest_use_distance_1_fn(fn, fns):
    cc = time.time()
    y = features_g_df.loc[fn].values.reshape(1, -1)
    best_score = 1e10
    best_match = "No match found"
    for fn_iter in tqdm.tqdm(fns):
        if fn_iter != fn:
            x = features_g_df.loc[fn_iter].values.reshape(1, -1)
            score = 1 - cosine_similarity(y, x)
            if best_score > score:
                best_match = fn_iter
                best_score = score
    return {"best_match": best_match, "score": best_score, "time":time.time()-cc}

def get_google_feature(fn):
    feature = features_g_df.loc[fn]
    return feature

def cosine_distance_GVision_PCA(fn1, fn2):
    x1 = features_g_df.loc[fn1].values.reshape(1, -1)
    x2 = features_g_df.loc[fn2].values.reshape(1, -1)
    dist = 1 - cosine_similarity(x1, x2)
    print("Cosine distance on GVision features for {}, {} = {}".format(fn1, fn2, dist))
    return dist


'''
Distance 2: Color distance in RGB space
'''
def get_nearest_use_distance_2_fn(fn, fns):
    cc = time.time()
    # fn = os.path.join(path, fn)
    # fns = [os.path.join(path, f) for f in fns]
    y = get_dominant_color(fn)
    best_score = 1e10
    best_match = "No match found"
    for fn_iter in tqdm.tqdm(fns):
        if fn_iter != fn:
            x = get_dominant_color(fn_iter)
            score = color_distance(y, x)
            if best_score > score:
                best_match = fn_iter
                best_score = score
    return {"best_match": best_match, "score": best_score, "time":time.time()-cc}


def get_dominant_color(fn):
    color = color_pkl[fn]
    return color

def get_dominant_color_deprecated(fn):
    if path not in fn:
        fn = os.path.join(path, fn)
    with io.open(fn, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.image_properties(image=image)
    colors = response.image_properties_annotation.dominant_colors.colors
    colors = np.array([(color.pixel_fraction, color.color.red, color.color.green, color.color.blue)
                        for color in colors])
    return np.sort(colors, axis=0)[::-1]


def color_distance(colors1, colors2):
    dist = 0
    for c1 in colors1:
        if c1[0]<0.05:
            continue
        tmp_dist = []
        for c2 in colors2:
            if c1[0]<0.05:
                continue
            dR, dG, dB = c1[1]-c2[1], c1[2]-c2[2], c1[3]-c2[3]
            fraction_weight = c1[0]*c2[0]
            r_mean = (c1[1] + c2[1]) / 2
            dcolor = np.sqrt((2+r_mean/256)*dR**2 + 4*dG**2 + (3-r_mean/256)*dB**2)
            tmp_dist.append([dcolor, fraction_weight])
        best_dcolor = np.sort(tmp_dist, axis=0)[0]  # pick the closest color pair
        dist += best_dcolor[0] * best_dcolor[1]
    #print("Color distance for {}, {} = {}".format(fn1, fn2, dist))
    return dist


'''
Distance 3: Cosine distance on rawdata (center cropping)
'''

def get_nearest_use_distance_3_fn(fn, fns):
    cc = time.time()
    fns = list(set(fns) - set([fn]))
    y = get_pooled_img(fn)
    scores = []
    for fn_iter in tqdm.tqdm(fns):
        x = get_pooled_img(fn_iter)
        score = cosine_distance_raw_center_crop(y, x)
        scores.append(score)
    min_pos = np.argsort(scores)[0]
    return {"best_match": fns[min_pos], "score": scores[min_pos], "time":time.time()-cc}


def get_pooled_img(fn):
    feature = pooling_df.loc[fn]
    return feature.values.reshape([1, -1])

def get_nearest_use_distance_3_fn_deprecated(fn, fns):
    cc = time.time()
    fns = list(set(fns) - set([fn]))
    fn = os.path.join(path, fn)
    fns = [os.path.join(path, f) for f in fns]
    y = get_pic_array(fn)
    scores = []
    for fn_iter in tqdm.tqdm(fns):
        x = get_pic_array(fn_iter)
        score = cosine_distance_raw_center_crop(y, x)
        scores.append(score)
    min_pos = np.argsort(scores)[0]
    return {"best_match": fns[min_pos], "score": scores[min_pos], "time":time.time()-cc}

def crop_to_square(pic_array1, pic_array2):
    a1, b1 = pic_array1.shape[0: 2]
    a2, b2 = pic_array2.shape[0: 2]
    c = min(a1, b1, a2, b2)/2
    c1 = pic_array1[int(a1/2 - c):int(a1/2 + c), int(b1/2 - c):int(b1/2 + c)]
    c2 = pic_array2[int(a2/2 - c):int(a2/2 + c), int(b2/2 - c):int(b2/2 + c)]
    return c1, c2


def get_pic_array(img_filename, res=32, use_dask=True):
    import dask_image.imread
    if use_dask:
        im = dask_image.imread.imread(img_filename)[0]
        pic = im.mean(axis=2)[::im.shape[0]//res, ::im.shape[1]//res][:res, :res]
    else:
        with Image.open(img_filename) as im:
            pic = np.array(im.getdata()).reshape(im.size[0], im.size[1], 3)
    return pic


def cosine_distance_raw_center_crop(pic1, pic2, use_dask=True):
    if use_dask:
        dist = 1 - np.mean(cosine_similarity(pic1, pic2))
    else:
        x1, x2 = crop_to_square(pic1, pic2)
        dist = 1 - np.mean([cosine_similarity(x1[:,:,layer], x2[:,:,layer]) for layer in range(1)])
        # print("Cosine distance on rawdata (center crop) for {}, {} = {}".format(fn1, fn2, dist))
    return dist

'''
Distance 4: Cosine distance on rawdata (center cropping)
'''

def get_nearest_use_distance_4_fn(fn, fns):
    cc = time.time()
    fns = list(set(fns) - set(fn))
    y = get_pooled_img(fn)
    scores = []
    for fn_iter in tqdm.tqdm(fns):
        x = get_pooled_img(fn_iter)
        score = euclidean_distance_raw_center_crop(y, x)
        scores.append(score)
    min_pos = np.argsort(scores)[0]
    return {"best_match": fns[min_pos], "score": scores[min_pos], "time":time.time()-cc}


def get_nearest_use_distance_4_fn_deprecated(fn, fns):
    cc = time.time()
    fns = list(set(fns) - set(fn))
    fn = os.path.join(path, fn)
    fns = [os.path.join(path, f) for f in fns]
    y = get_pic_array(fn)
    best_match = "Not found"
    best_score = 1e10
    for fn_iter in tqdm.tqdm(fns):
        x = get_pic_array(fn_iter)
        score = euclidean_distance_raw_center_crop(y, x)
        if best_score > score:
            best_score = score
            best_match = fn_iter
    return {"best_match": best_match, "score": score, "time":time.time()-cc}


def euclidean_distance_raw_center_crop(pic1, pic2, use_dask=True):
    if use_dask:
        dist = np.mean(MSE(pic1, pic2))
    else:
        x1, x2 = crop_to_square(pic1, pic2)
        dist = 1 - np.mean([cosine_similarity(x1[:,:,layer], x2[:,:,layer]) for layer in range(1)])
        # print("Cosine distance on rawdata (center crop) for {}, {} = {}".format(fn1, fn2, dist))
    return dist
