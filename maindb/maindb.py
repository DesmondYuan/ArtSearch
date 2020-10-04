from flask import Flask, render_template, request
import pandas as pd
import os

from query import get_metadata, get_google_feature, get_dominant_color, get_nearest


app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def mainm():

    if request.method == "POST":
        filename = request.get_json()["art_image"]
        fullfilename = os.path.join("img", filename)
        meta = get_metadata(filename)
        google_features = get_google_feature(filename)
        dominant_colors = get_dominant_color(
            filename
        )  # comment out this line for faster calculation
        nearest = get_nearest(filename)
        df = pd.DataFrame(nearest)
        match1 = os.path.join("img", df.loc["best_match", "distance_1"])
        match2 = os.path.join("img", df.loc["best_match", "distance_2"])
        match3 = os.path.join("img", df.loc["best_match", "distance_3"])
        match4 = os.path.join("img", df.loc["best_match", "distance_4"])

        # md = pd.DataFrame(meta, columns=["Descriptor", "Value"])

        return render_template(
            "display.html",
            art_image=fullfilename,
            match1=match1,
            match2=match2,
            match3=match3,
            match4=match4,
            google_features=str(google_features),
            dominant_colors=str(dominant_colors),
            nearest_images=str(nearest),
            metadata=[meta.to_html(classes="data")]
            # metadata="<html><head>Painting Information</head><body>"
            # + meta
            # + "</body></html>",
            # md=(md),
        )

        # return render_template(
        #     "metadata.html",
        #     tables=[meta.to_html(classes="data")],
        #     titles=meta.columns.values,
        # )
    else:
        return "maindb.py - This is get method - try using post -- "


if __name__ == "__main__":
    # from dask.distributed import Client
    # client = Client()
    # print("Dask client started: ", client)
    app.run(host="0.0.0.0", port=8082, debug=True)

