from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)


def get_language():
    return request.args.get("lang") or request.form.get("lang", "es")


def error_message(lang):
    if lang == "es":
        return "Los archivos no son válidos. Sube followers_1.json y following.json descargados de Instagram."
    return "The files are not valid. Upload followers_1.json and following.json downloaded from Instagram."


def extension_error_message(lang):
    if lang == "es":
        return "Solo se permiten archivos .json"
    return "Only .json files are allowed"


def is_json_file(file):
    return file.filename.lower().endswith(".json")


def load_json_file(file):
    return json.load(file)


def extract_followers(data):
    usernames = []

    for item in data:
        string_data = item.get("string_list_data", [])

        if string_data:
            username = string_data[0].get("value")

            if username:
                usernames.append(username)

    return usernames


def extract_following(data):
    usernames = []

    for item in data.get("relationships_following", []):
        username = item.get("title")

        if username:
            usernames.append(username)

    return usernames


def compare_users(followers, following):
    followers_set = set(followers)
    following_set = set(following)

    return {
        "not_following_back": sorted(following_set - followers_set),
        "fans": sorted(followers_set - following_set),
        "mutuals": sorted(followers_set & following_set),
    }


@app.route("/", methods=["GET"])
def index():
    lang = get_language()
    return render_template("index.html", lang=lang)


@app.route("/compare", methods=["POST"])
def compare():
    lang = get_language()

    try:
        followers_file = request.files["followers"]
        following_file = request.files["following"]

        if not is_json_file(followers_file) or not is_json_file(following_file):
            return render_template(
                "index.html",
                lang=lang,
                error=extension_error_message(lang)
            )

        followers_data = load_json_file(followers_file)
        following_data = load_json_file(following_file)

        followers = extract_followers(followers_data)
        following = extract_following(following_data)

        results = compare_users(followers, following)

        return render_template(
            "result.html",
            not_following_back=results["not_following_back"],
            fans=results["fans"],
            mutuals=results["mutuals"],
            lang=lang
        )

    except (KeyError, TypeError, IndexError, json.JSONDecodeError):
        return render_template(
            "index.html",
            lang=lang,
            error=error_message(lang)
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))