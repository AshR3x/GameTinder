from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/games')
def games():
    page = request.args.get('page', default=0, type=int)
    if page <= 0:
        res = requests.get("https://steamspy.com/api.php?request=top100in2weeks")
    else:
        res = requests.get(f"https://steamspy.com/api.php?request=all&page={page - 1}")
    return jsonify(res.json())

@app.route('/game/<int:appid>')
def game_details(appid):
    res = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")
    data = res.json()
    game = data[str(appid)].get('data', {})
    return jsonify({
        'description': game.get('short_description', 'No description available.'),
        'genres': [g['description'] for g in game.get('genres', [])],
        'categories': [c['description'] for c in game.get('categories', [])][:4],
        'screenshots': [s['path_full'] for s in game.get('screenshots', [])]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)