from prometheus_client import Metric
from storage import MetricStore


class StoreCollector(object):
    def __init__(self):
        self.store = MetricStore()

    def collect(self):
        for job, sample_list in self.store:
            prometheus_metric = Metric(job, "Metric set from collector module", "summary")
            for metric_sample in sample_list:
                metric_name, metric_value, metric_labels = metric_sample.values()
                prometheus_metric.add_sample(metric_name, metric_labels, metric_value)
            yield prometheus_metric
