from entry.models import Lap
from entry.services.entry_base import Entry

import pandas as pd
from funcy import log_durations
import logging


class EntryCsv(Entry):
    """Entry csv class
    process .csv files and store data in db
    """

    def __init__(self, *args, **kwargs):
        super(EntryCsv, self).__init__(*args, **kwargs)

    @log_durations(logging.info)
    def get_dataframe_from_file(self, file_path: str):
        """Get dataframe from file"""
        df = pd.read_csv(file_path)
        df['Time'] = pd.to_timedelta(df['Time']).dt.total_seconds()
        df['Moving Time'] = pd.to_timedelta(df['Moving Time']).dt.total_seconds()
        return df

    @log_durations(logging.info)
    def dataframe_to_model_objs(self, df: pd.DataFrame):
        """Dataframe to model objs"""
        return [
            Lap(
                user_id=self.entry.customer.id,
                entry_id=self.entry.id,
                total_distance=row['Distance'],
                total_elapsed_time=row['Moving Time'],
            ) for index, row in df.iterrows()
        ]

    @log_durations(logging.info)
    def submit_model_objs_to_db(self, model_objs: list):
        """Submit model objs to db"""
        Lap.objects.bulk_create(model_objs)

    def run(self):
        """Run"""
        file_path = self.entry.file.path
        df = self.get_dataframe_from_file(file_path)
        model_objs = self.dataframe_to_model_objs(df)
        self.submit_model_objs_to_db(model_objs)
