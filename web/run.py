from flask import Flask
from flask import render_template
import os,json
app=Flask(__name__)

@app.route('/')
def index(name=None):
    config=getConfig()
    print(config)
    return render_template('index.html',config=config)

def getConfig():
    filename = os.path.join(app.static_folder,  os.path.abspath(os.path.dirname(__file__))+'/config.json')
    with open(filename) as blog_file:
        data = json.load(blog_file)
    return data

if __name__=='__main__':
    app.run(8000,debug=False)