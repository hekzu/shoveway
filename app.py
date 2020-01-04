from prometheus_client import REGISTRY, generate_latest
from flask import Flask, Response, request
from collector import StoreCollector
from argparse import ArgumentParser
from config import Configuration
from storage import MetricStore
from sample import Sample
import json
import os


app = Flask(__name__)


@app.route('/metrics', methods=['GET'])
def serve_metrics():
    return generate_latest(REGISTRY)


@app.route('/sample/<job>', methods=['POST'])
def receive_sample(job):
    sample_data = json.loads(request.data)
    try:
        sample = Sample.from_json(sample_data)
    except TypeError as e:
        return Response(status=400, response=str(e))
    if sample is None:
        return Response(status=400, response="Invalid JSON document.")
    store.put(job, sample)
    return Response(status=200)


def validate_config_path(arguments):
    try:
        path = arguments['path']
    except KeyError:
        return False
    if path and not os.path.isfile(path):
        raise OSError("Invalid path to configuration file")


def main(arguments):
    if validate_config_path(arguments):
        config = Configuration(arguments['path'])
    else:
        config = Configuration

    global store
    store = MetricStore(persist=config.persist)

    collector = StoreCollector()
    REGISTRY.register(collector)

    try:
        app.run(
            host=config.host,
            port=config.port,
            threaded=config.threaded,
            use_reloader=config.reloader
        )
    except PermissionError:
        print(f"Port '{config.port}' is either taken or reserved by the system.")
        print("Please choose a different port or provide elevated permissions.")
        exit(1)
    except ValueError:
        print(f"'{config.port}' is not a valid port.")
        exit(1)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to configuration file", required=False)

    args = vars(parser.parse_args())
    main(args)
