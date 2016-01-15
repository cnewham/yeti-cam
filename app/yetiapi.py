from app import app

@app.route('/api')
def api():
    return "Hello, World from API!"