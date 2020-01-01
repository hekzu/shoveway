from prometheus_client import REGISTRY, Metric, generate_latest
from flask import Flask, Response, request
from argparse import ArgumentParser
from storage import MetricStore
from sample import Sample
import json


app = Flask(__name__)
store = MetricStore(persist=True)


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


class GenericCollector(object):
    def __init__(self):
        self.store = MetricStore()

    def collect(self):
        for job, metric in self.store:
            prometheus_metric = Metric(job, "Metric set from collector module", "summary")
            for metric_sample in metric:
                metric_name, metric_value, metric_labels = metric_sample.values()
                prometheus_metric.add_sample(metric_name, metric_labels, metric_value)
            yield prometheus_metric


def main(arguments):
    collector = GenericCollector()
    REGISTRY.register(collector)

    try:
        app.run(
            host="0.0.0.0",
            port=arguments["port"],
            threaded=False,
            use_reloader=False
        )
    except PermissionError:
        print(f"Port '{arguments['port']}' is either taken or reserved by the system.")
        print("Please choose a different port or provide elevated permissions.")
        exit(1)
    except ValueError:
        print(f"'{arguments['port']}' is not a valid port.")
        exit(1)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", help="Port number over which the metrics will be served.", required=True)

    args = vars(parser.parse_args())
    main(args)
