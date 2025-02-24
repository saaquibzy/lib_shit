from flask import Flask
from routes import app_routes

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

# Register the Blueprint
app.register_blueprint(app_routes, url_prefix="/")

if __name__ == "__main__":
    app.run(debug=True)
