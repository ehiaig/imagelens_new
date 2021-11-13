import config
from flask_cors import CORS
import os 
DEPLOYMENT_TYPE = os.getenv("DEPLOYMENT_TYPE") or "test"

app = config.connexion_app
app.add_api("spec.yaml", strict_validation=True)
# app.add_api("spec.yaml", base_path="/", validate_responses=DEPLOYMENT_TYPE != "master")

cors = CORS(
    app.app,
    resources=r"/*",
    origins=[
        "http://imagelens.ai",
    ],
    max_age=5000,
)

app.run(port=8080, debug=True)