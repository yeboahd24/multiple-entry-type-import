from entry.models import Point, Lap
from entry.services.entry_base import Entry

from typing import Dict, Optional
import pandas as pd
import fitdecode
from funcy import log_durations
import logging


class EntryFit(Entry):
    """Entry fit class
    process .fit files and store data in db
    """
    __points_column_names = ['latitude', 'longitude', 'lap', 'altitude', 'timestamp', 'heart_rate', 'cadence', 'speed']
    __laps_column_names = ['number', 'start_time', 'total_distance', 'total_elapsed_time',
                           'max_speed', 'max_heart_rate', 'avg_heart_rate']

    def __init__(self, *args, **kwargs):
        super(EntryFit, self).__init__(*args, **kwargs)

    def __get_fit_point_data(self, frame: fitdecode.records.FitDataMessage) -> Optional[Dict]:
        data = {}

        if not (frame.has_field('position_lat') and frame.has_field('position_long')):
            # Frame does not have any latitude or longitude data. We will ignore these frames in order to keep things
            # simple, as we did when parsing the TCX file.
            return None
        else:
            if frame.get_value('position_lat') and frame.get_value('position_long'):
                data['latitude'] = frame.get_value('position_lat') / ((2 ** 32) / 360)
                data['longitude'] = frame.get_value('position_long') / ((2 ** 32) / 360)

        for field in self.__points_column_names[3:]:
            if frame.has_field(field):
                data[field] = frame.get_value(field)

        return data

    def __get_fit_lap_data(self, frame: fitdecode.records.FitDataMessage) -> Dict:
        data = {}

        for field in self.__laps_column_names[1:]:  # Exclude 'number' (lap number) because we don't get that
            # from the data but rather count it ourselves
            if frame.has_field(field):
                data[field] = frame.get_value(field)
            else:
                data[field] = None

        return data

    def __points_to_model_objs(self, df: pd.DataFrame) -> list:
        return [
            Point(
                user_id=self.entry.customer.id,
                entry_id=self.entry.id,
                latitude=row['latitude'],
                longitude=row['longitude'],
                lap_number=row['lap'],
                altitude=row['altitude'],
                timestamp=row['timestamp'],
                heart_rate=row['heart_rate'],
                cadence=row['cadence'],
                speed=row['speed']
            ) for index, row in df.iterrows()
        ]

    def __laps_to_model_objs(self, df: pd.DataFrame) -> list:
        return [
            Lap(
                user_id=self.entry.customer.id,
                entry_id=self.entry.id,
                number=row['number'],
                start_time=row['start_time'],
                total_distance=row['total_distance'],
                total_elapsed_time=row['total_elapsed_time'],
                max_speed=row['max_speed'],
                max_heart_rate=row['max_heart_rate'],
                avg_heart_rate=row['avg_heart_rate']
            ) for index, row in df.iterrows()
        ]

    @staticmethod
    def __bulk_insert_points(points: list):
        """Bulk insert points"""
        Point.objects.bulk_create(points)

    @staticmethod
    def __bulk_insert_laps(laps: list):
        """Bulk insert laps"""
        Lap.objects.bulk_create(laps)

    @log_durations(logging.info)
    def get_dataframe_from_file(self, file_path: str) -> (pd.DataFrame, pd.DataFrame):
        """Get dataframe from file"""
        points_data = []
        laps_data = []
        lap_no = 1
        with fitdecode.FitReader(file_path) as fit_file:
            for frame in fit_file:
                if isinstance(frame, fitdecode.records.FitDataMessage):
                    if frame.name == 'record':
                        single_point_data = self.__get_fit_point_data(frame)
                        if single_point_data is not None:
                            single_point_data['lap'] = lap_no
                            points_data.append(single_point_data)
                    elif frame.name == 'lap':
                        single_lap_data = self.__get_fit_lap_data(frame)
                        single_lap_data['number'] = lap_no
                        laps_data.append(single_lap_data)
                        lap_no += 1

        # Create DataFrames from the data we have collected. If any information is missing from a particular lap or
        # track point, it will show up as a null value or "NaN" in the DataFrame.

        laps_df = pd.DataFrame(laps_data, columns=self.__laps_column_names)
        points_df = pd.DataFrame(points_data, columns=self.__points_column_names)
        return laps_df, points_df

    @log_durations(logging.info)
    def dataframe_to_model_objs(self, df: pd.DataFrame) -> list:
        """Dataframe to model objs"""
        if df.columns.tolist() == self.__points_column_names:
            return self.__points_to_model_objs(df)
        else:
            return self.__laps_to_model_objs(df)

    @log_durations(logging.info)
    def submit_model_objs_to_db(self, model_objs: list):
        """Submit model objs to db"""
        if isinstance(model_objs[0], Point):
            self.__bulk_insert_points(model_objs)
        elif isinstance(model_objs[0], Lap):
            self.__bulk_insert_laps(model_objs)
        else:
            raise TypeError('model_objs must be a list of Point or Lap objects')

    def run(self):
        """Run"""
        laps_df, points_df = self.get_dataframe_from_file(self.entry.file.path)
        points_objs = self.dataframe_to_model_objs(points_df)
        laps_objs = self.dataframe_to_model_objs(laps_df)
        self.submit_model_objs_to_db(points_objs)
        self.submit_model_objs_to_db(laps_objs)
