from abc import ABC, abstractmethod
import pandas as pd


class Entry(ABC):
    """Entry base class"""
    def __init__(self, entry, *args, **kwargs):
        self.entry = entry
        super(Entry, self).__init__(*args, **kwargs)

    @abstractmethod
    def get_dataframe_from_file(self, file_path: str):
        """Get dataframe from file"""
        raise NotImplementedError("get_dataframe() is not implemented")

    @abstractmethod
    def dataframe_to_model_objs(self, df: pd.DataFrame):
        """Dataframe to model objs"""
        raise NotImplementedError("dataframe_to_model_objs() is not implemented")

    @abstractmethod
    def submit_model_objs_to_db(self, model_objs: list):
        """Submit model objs to db"""
        raise NotImplementedError("submit_model_objs_to_db() is not implemented")

    @abstractmethod
    def run(self):
        raise NotImplementedError("run() is not implemented")
