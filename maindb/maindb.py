from flask import Flask, render_template, request
import os
from query import get_metadata, get_google_feature, get_dominant_color, get_nearest

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def mainm():

    # if request.method == "POST":
    #     filename = request.get_json()["art_image"]
    #     meta = get_metadata(filename)
    #     google_features = get_google_feature(filename)
    #     dominant_colors = get_dominant_color(filename)
    #     nearest = get_nearest(filename)
    #     msg = "\nLoading filename successful! Now we are at root:" + os.getcwd()

    #     return render_template(
    #         "display.html",
    #         art_image=filename,
    #         msg=msg,
    #         google_features=str(google_features),
    #         dominant_colors=str(dominant_colors),
    #         nearest_images=str(nearest),
    #     )

    if request.method == "POST":
        filename = request.get_json()["art_image"]
        msg = "\nLoading filename successful! Now we are at root:" + os.getcwd()
        return render_template("display.html", art_image=filename, msg=msg)

    else:
        return "maindb.py - This is get method - try using post -- "


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)
