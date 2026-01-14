import os
import traceback
import dotenv
from flask import Flask, jsonify
from skillweaver.containerization.containers import Orchestrator, container_specs
dotenv.load_dotenv()
app = Flask(__name__)

# Initialize the Containerization class
containerization = Orchestrator(
    start_port=8000, container_hostname=os.getenv("IP", "127.0.0.1")
)


@app.route("/obtain/<image_name>", methods=["GET"])
def obtain_container(image_name):
    if image_name not in container_specs:
        return jsonify({"error": f"Invalid image name: {image_name}"}), 400

    try:
        container, port = containerization.obtain_container(image_name)

        return (
            jsonify(
                {"host": os.getenv("IP", "127.0.0.1"), "port": port, "id": container.id}
            ),
            200,
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/release/<container_id>", methods=["GET"])
def release_container(container_id):
    try:
        containerization.release_container(container_id)

        return (
            jsonify({"message": f"Container {container_id} released successfully"}),
            200,
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/status", methods=["GET"])
def get_status():
    status = {
        "running_containers": list(containerization.active),  # len(container_tracker),
        "available_images": list(container_specs.keys()),
    }
    return jsonify(status), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0", port=int(os.getenv("ORCHESTRATOR_PORT") or 5125), debug=False
    )
