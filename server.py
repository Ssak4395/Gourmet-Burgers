from GourmetBurgers import GBSystem
from flask import Flask
import routes

# Create Flask instance
app = Flask(__name__, template_folder='./site/templates',
            static_folder='./site/assets', static_url_path='/assets')

# Initialise GBSystem, and bind it to Flask
app.GB = GBSystem()

# Register routes
for module in routes.__modules:
    app.register_blueprint(routes.__modules[module].site)

# Start server
app.run("0.0.0.0", 1313, debug=True)
