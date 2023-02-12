### 参考URL：https://aiacademy.jp/media/?p=57

from flask import Flask

# HTMLのディレクトリ
html_dir = "./templates/"
app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    index_html = html_dir + 'index.html'
    return app.send_static_file(index_html) # 静的に決まっているHTMLファイルを返す

@app.route('/hello/<name>')
def hello(name):
    print(name) # <- localhost:8000/hello/<name> 部分
    return name

app.run(port=8000, debug=True)
