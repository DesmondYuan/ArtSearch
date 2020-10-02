from flask import Flask, render_template, request
import os

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

        full_filename = os.path.join("/gap_images/gap_images/", record)

        ### TEMPORARY HARD CODE
        return render_template("display.html", art_image=full_filename)
        # return "This is the filename you requested: " + str(full_filename)
    else:
        return "maindb.py - This is get method - try using post -- "


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)
