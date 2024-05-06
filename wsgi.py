from app import app, app_port

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=app_port, debug=False)