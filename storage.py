from singleton_decorator import singleton
from threading import Thread, Event
from sample import Sample
import schedule
import json
import time
import os


STORE_FILE_PATH = "store.json"
READ_MODE = "r"
WRITE_MODE = "w"
FLUSH_INTERVAL_SECONDS = 5


class MetricStoreIterator(object):
    def __init__(self, metric_store):
        self._store = metric_store
        self._jobs = metric_store.jobs()
        self._index = 0

    def __next__(self):
        if self._index >= len(self._jobs):
            raise StopIteration
        job = self._jobs[self._index]
        self._index += 1
        return job, self._store.get(job)


@singleton
class MetricStore(object):
    def __init__(self, persist=False):
        self.persist = persist
        if self.persist:
            store_dump = self.__read__()
            self.store = store_dump if store_dump else {}
            schedule.every(FLUSH_INTERVAL_SECONDS).seconds.do(self.__flush__)

            self.__run_event = Event()
            self.__run_event.set()

            self.__schedule_thread = Thread(target=self.__run_pending__, args=(self.__run_event, ))
            self.__schedule_thread.start()
        else:
            self.store = {}

    def __iter__(self):
        return MetricStoreIterator(self)

    @staticmethod
    def __run_pending__(run_event):
        while run_event.is_set():
            schedule.run_pending()
            time.sleep(FLUSH_INTERVAL_SECONDS)

    def __read__(self):
        loaded_store = {}
        store_json = self.__load_from_disk__()
        for job in store_json.keys():
            sample_list = store_json[job]
            loaded_store[job] = [Sample.from_json(sample_json) for sample_json in sample_list]
        return loaded_store

    def __flush__(self):
        store_dict = {}
        job_list = self.jobs()
        for job in job_list:
            sample_list = self.get(job)
            store_dict[job] = [sample.to_json() for sample in sample_list]

        self.__dump_to_disk__(store_dict)

    @staticmethod
    def __load_from_disk__():
        if os.path.isfile(STORE_FILE_PATH):
            persistence_file = open(STORE_FILE_PATH, READ_MODE)
            store_file_content = persistence_file.read()
            if store_file_content and store_file_content != "":
                return json.loads(store_file_content)
        return {}

    @staticmethod
    def __dump_to_disk__(store_json):
        persistence_file = open(STORE_FILE_PATH, WRITE_MODE)
        persistence_file.write(json.dumps(store_json))

    def values(self):
        return self.store.values()

    def jobs(self):
        return list(self.store.keys())

    def put(self, job, sample):
        if job not in self.store.keys():
            self.store[job] = []
        if type(sample) is not Sample:
            raise TypeError("Value must be of Sample type.")
        self.store[job].append(sample)

    def get(self, job):
        return self.store[job]
