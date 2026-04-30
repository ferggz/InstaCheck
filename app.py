from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

def extract_followers(data):
    usernames = []

    for item in data:
        username = item["string_list_data"][0]["value"]
        usernames.append(username)

    return usernames

def extract_following(data):
    usernames = []

    for item in data["relationships_following"]:
        username = item["title"]
        usernames.append(username)

    return usernames

@app.route("/compare", methods=["POST"])
def compare():
    lang = request.form.get("lang", "es")

    try:
        followers_file = request.files["followers"]
        following_file = request.files["following"]

        if not followers_file.filename.endswith(".json") or not following_file.filename.endswith(".json"):
            return render_template(
                "index.html",
                lang=lang,
                error="Solo se permiten archivos .json" if lang == "es" else "Only .json files are allowed"
            )

        followers_data = json.load(followers_file)
        following_data = json.load(following_file)

        followers = extract_followers(followers_data)
        following = extract_following(following_data)

        not_following_back = sorted(set(following) - set(followers))
        fans = sorted(set(followers) - set(following))
        mutuals = sorted(set(followers) & set(following))

        return render_template(
            "result.html",
            not_following_back=not_following_back,
            fans=fans,
            mutuals=mutuals,
            lang=lang
        )

    except (KeyError, TypeError, IndexError, json.JSONDecodeError):
        return render_template(
            "index.html",
            lang=lang,
            error="Los archivos no son válidos. Sube followers_1.json y following.json descargados de Instagram."
            if lang == "es"
            else "The files are not valid. Upload followers_1.json and following.json downloaded from Instagram."
        )

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))