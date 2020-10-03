from flask import Flask, render_template, request
import os
import pandas as pd
import numpy as np
from google.cloud import vision
import io

os.system("export GOOGLE_APPLICATION_CREDENTIALS='/resource/google_api_auth.json'")
client = vision.ImageAnnotatorClient()
features_g_df = pd.read_csv("/resource/FeatureTable_GoogleAnnot.PCA.csv", index_col=0)
def read_color(fn):
    with io.open(fn, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.image_properties(image=image)
    colors = response.image_properties_annotation.dominant_colors.colors
    return [(color.pixel_fraction, color.color.red, color.color.green, color.color.blue)
            for color in colors]

# PEOPLE_FOLDER = os.path.join('static', 'people_photo')

app = Flask(__name__)
# app.config["IMAGE_FOLDER"] =

# @app.route("/display")
# def show_index():
#     full_filename = os.path.join("gap_images/gap_images/", "gap_11111.jpg")
#     return render_template("display.html", art_image=full_filename)


@app.route("/", methods=["POST", "GET"])
def mainm():

    if request.method == "POST":
        # Retrieve the art_image submitted by the user. Get the image corresponding
        # to this id and return it back to the user.
        record = request.get_json()["art_image"]
        full_filename = os.path.join('/resource/img/', record)
        msg = "\nNow we are at" + os.getcwd()
        google_features = features_g_df.loc[record]
        dominant_colors = read_color(full_filename)
        # TODO: adding try/except for flask

        ### TEMPORARY HARD CODE
        return render_template("display.html", art_image=full_filename, msg=msg,
                                google_features=google_features, dominant_colors=dominant_colors)
        # return "This is the filename you requested: " + str(full_filename)
    else:
        return "maindb.py - This is get method - try using post -- "


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)
