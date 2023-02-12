### 参考URL：https://aiacademy.jp/media/?p=57

import os
from flask import Flask, url_for, render_template, request
import flask

# # HTMLのディレクトリ
# html_dir = "./templates/"
# render_templateを使うといらない。

app = Flask(__name__)

# ルーティング
@app.route("/hello") 
def hello_world():
    """
    テスト用

    Returns:
        _type_: この場合の型は何だ？？
    """
    return "Hello world"

# @app.route("/")
# def index():
#     """
#     ルートディレクトリにおける挙動

#     Returns:
#         _type_: _description_
#     """
#     return url_for("show_user_profile", username="test_flack")

# @app.route("/")
# def index():
#     """
#     最初に表示されるページ

#     Returns:
#         _type_: _description_
#     """
#     return render_template('index.html', message = "神")

@app.route("/", methods = ['GET', 'POST'])
def form():
    """
    プロジェクト名と内容の入力
    他工程でも使いたい
    工程に応じて表示が必要なものをif分で条件分岐するイメージ？ここは要相談かも
    """
    # 2回目以降データが送られてきた時の処理
    if request.method == 'POST':
        # 送られてきた内容まとめ
        project_data = {
            "PROJECT_NAME": str(request.form['project_name']),
            "PROJECT_SUMMARY": str(request.form['summary'])
        }        

        # printじゃなくてLogger使ってもいいかも。
        print(f"プロジェクト名: {project_data['PROJECT_NAME']}")
        print(f"内容: {project_data['PROJECT_SUMMARY']}")

        return flask.jsonify({
        "code": 200,
        "msg" : "OK",
        "result": project_data
    })

    # 1回目のデータが何も送られてこなかった時の処理
    else:
        return render_template('form.html')


if __name__ == "__main__":
    app.run(port=8000, debug=True)