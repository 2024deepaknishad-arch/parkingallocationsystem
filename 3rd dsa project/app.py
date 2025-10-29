# app.py (entry point)
from flask import Flask
from routes.parking_routes import parking_bp
from routes.api_routes import api_bp
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(parking_bp, url_prefix="/")
app.register_blueprint(api_bp, url_prefix="/api")

# Auto-generate README on first run
from utils.readme_gen import generate_readme
generate_readme()

if __name__ == "__main__":
    app.run(debug=True)