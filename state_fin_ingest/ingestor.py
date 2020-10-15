class Ingestor:
    def __init__(self, parent):
        # Gives ingestor access to parent data that might be shared
        self.parent = parent

    @property
    def required_files(self):
        return []

    def pre(self):
        raise NotImplementedError

    def work(self):
        raise NotImplementedError

    def post(self):
        pass

class RootIngestor:
    def __init__(self):
        if self.contrib_ingestor_class:
            self.contrib_ingestor = self.contrib_ingestor_class(self)
        
        if self.report_ingestor_class:
            self.report_ingestor = self.report_ingestor_class(self)

    @property
    def required_files(self):
        return []

    def pre(self):
        raise NotImplementedError

    def post(self):
        pass

    @property
    def ingest_prefix(self):
        raise NotImplementedError

    @property
    def contrib_ingestor_class(self):
        return None

    @property
    def report_ingestor_class(self):
        return None