from flask import Flask, render_template, request
import os
from utils import query

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def mainm():

    if request.method == "POST":
        filename = request.get_json()["art_image"]
        meta = query.get_metadata(filename)
        google_features = query.get_google_feature(filename)
        dominant_colors = query.get_dominant_color(filename)
        nearest = get_nearest(filename)
        msg = "\nLoading filename successful! Now we are at root:" + os.getcwd(filename)

        return render_template("display.html", art_image=full_filename, msg=msg,
                                google_features=str(google_features), dominant_colors=str(dominant_colors),
                                nearest_images=str(nearest))
    else:
        return "maindb.py - This is get method - try using post -- "


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)
