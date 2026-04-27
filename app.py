from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

def extract_usernames(data):
    usernames = []

    for item in data:
        if "string_list_data" in item and item["string_list_data"]:
            username = item["string_list_data"][0]["value"]
            usernames.append(username)

    return usernames

@app.route("/compare", methods=["POST"])
def compare():
    followers_file = request.files["followers"]
    following_file = request.files["following"]

    followers_data = json.load(followers_file)
    following_data = json.load(following_file)

    followers = extract_usernames(followers_data)
    following = extract_usernames(following_data)

    not_following_back = sorted(set(following) - set(followers))
    fans = sorted(set(followers) - set(following))
    mutuals = sorted(set(followers) & set(following))

    return render_template(
        "result.html",
        not_following_back=not_following_back,
        fans=fans,
        mutuals=mutuals
    )

if __name__ == "__main__":
    app.run(debug=True)