class Ingestor:
    @property
    def required_files(self):
        raise NotImplementedError

    @property
    def ingest_prefix(self):
        raise NotImplementedError

    def pre(self):
        raise NotImplementedError

    def work(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError
