from flask import Flask, render_template, request, jsonify
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from websites.french.anime_sama import anime_sama

app = Flask(__name__)

@app.route('/')
def test():
    return render_template('index.html')


@app.route('/process_data', methods=['POST'])
def process_data():

    data = request.get_json()
    range_from = data.get('rangeFrom')
    range_to = data.get('rangeTo')
    quality = data.get('quality')
    version = data.get('version')
    url = data.get('url')

    range_from = 'start' if range_from==1 else range_from
    range_to = 'end' if range_to==50 else range_to



    a_s = anime_sama(preferred_version=version,resolution=quality)
    result = a_s.extract(url,range=(range_from,range_to),mode='return')
    print(result)
    return jsonify(output=result)

if __name__=='__main__':
    app.run()