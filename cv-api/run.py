from app import app

app.run(debug=True, host='0.0.0.0', port=5005, use_reloader=False, threaded=True)
