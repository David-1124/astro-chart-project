@app.route('/favicon.ico')
def favicon():
    return send_file('path/to/favicon.ico', mimetype='image/vnd.microsoft.icon')
