from flask import Flask,render_template
import commands


app = Flask(__name__,static_url_path='/static')



@app.route('/')
@app.route('/index.html')
def index_page():
    return render_template("index.html")

@app.route('/app.html')
def app_page():
    return render_template("app.html")

@app.route('/log.html')
def log_page():
    return render_template("log.html")


@app.route('/get_log')
def get_log():
    file = open('t.txt',"r")
    content = file.read().split("\n")
    min_length = min(15,len(content))
    content = content[-min_length:]
    string = ""
    for i in range(min_length):
        string = string + content[i] + "<br>"
    return string

if __name__ == '__main__':
    app.run()
