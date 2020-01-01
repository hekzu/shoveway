import json


class Sample(object):
    def __init__(self, name, value, labels=None):
        self.name = name
        self.value = value
        self.labels = labels

    def values(self):
        return self.name, self.value, self.labels

    def to_json(self):
        return {
            "name": self.name,
            "value": self.value,
            "labels": self.labels
        }

    @staticmethod
    def __parse_labels__(labels):
        if labels:
            if type(labels) is str:
                labels = json.loads(labels)
            if type(labels) is not dict:
                raise TypeError("Labels must be a dictionary.")

        return labels

    @staticmethod
    def from_json(sample_data):
        try:
            name = sample_data['name']
        except KeyError:
            return None
        try:
            value = float(sample_data['value'])
        except ValueError:
            raise TypeError("Metric value must be of type float.")
        labels = Sample.__parse_labels__(sample_data['labels'] if 'labels' in sample_data.keys() else None)

        return Sample(
            name,
            value,
            labels=labels
        )