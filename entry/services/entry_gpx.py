from entry.models import Point
from entry.services.entry_base import Entry

import pandas as pd
import gpxpy
from funcy import log_durations
import logging


class EntryGpx(Entry):
    """Entry gpx class
    process .gpx files and store data in db
    """
    __namespaces = {'garmin_tpe': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}
    __column_names = ['latitude', 'longitude', 'elevation', 'time', 'heart_rate', 'cadence']

    def __init__(self, *args, **kwargs):
        super(EntryGpx, self).__init__(*args, **kwargs)

    def __get_gpx_point_data(self, point):
        """Get gpx point data"""
        data = {
            'latitude': point.latitude,
            'longitude': point.longitude,
            'elevation': point.elevation,
            'time': point.time
        }

        # Parse extensions for heart rate and cadence data, if available
        if point.extensions:
            elem = point.extensions[0]  # Assuming we know there is only one extension
            try:
                data['heart_rate'] = int(elem.find('garmin_tpe:hr', self.__namespaces).text)
            except AttributeError:
                # "text" attribute not found, so data not available
                pass

            try:
                data['cadence'] = int(elem.find('garmin_tpe:cad', self.__namespaces).text)
            except AttributeError:
                pass

        return data

    @log_durations(logging.info)
    def get_dataframe_from_file(self, file_path: str):
        """Get dataframe from file"""
        with open(file_path) as f:
            gpx = gpxpy.parse(f)
        segment = gpx.tracks[0].segments[0]  # Assuming we know that there is only one track and one segment
        data = [self.__get_gpx_point_data(point) for point in segment.points]
        return pd.DataFrame(data, columns=self.__column_names)

    @log_durations(logging.info)
    def dataframe_to_model_objs(self, df: pd.DataFrame):
        """Dataframe to model objs"""
        return [
            Point(
                user_id=self.entry.customer.id,
                entry_id=self.entry.id,
                latitude=row['latitude'],
                longitude=row['longitude'],
                altitude=row['elevation'],
                timestamp=row['time'],
                heart_rate=row['heart_rate'],
                cadence=row['cadence']
            ) for index, row in df.iterrows()
        ]

    @log_durations(logging.info)
    def submit_model_objs_to_db(self, model_objs: list):
        """Submit model objs to db"""
        Point.objects.bulk_create(model_objs)

    def run(self):
        """Run"""
        df = self.get_dataframe_from_file(self.entry.file.path)
        model_objs = self.dataframe_to_model_objs(df)
        self.submit_model_objs_to_db(model_objs)
