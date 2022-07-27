from datetime import datetime, timedelta
from typing import Dict, Union, Optional

import lxml.etree
import dateutil.parser as dp
import pandas as pd
from funcy import log_durations
import logging

from entry.models import Lap, Point
from entry.services.entry_base import Entry


class EntryTcx(Entry):
    """Entry tcx class
    process .tcx files and store data in db
    """
    __namespaces = {
        'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
        'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
        'ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
        'ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1'
    }
    __points_column_names = ['latitude', 'longitude', 'elevation', 'time', 'heart_rate', 'cadence', 'speed', 'lap']
    __laps_column_names = ['number', 'start_time', 'distance', 'total_time', 'max_speed', 'max_hr', 'avg_hr']

    def __init__(self, *args, **kwargs):
        super(EntryTcx, self).__init__(*args, **kwargs)

    def __get_tcx_lap_data(self, lap: lxml.etree._Element) -> Dict[str, Union[float, datetime, timedelta, int]]:
        """Extract some data from an XML element representing a lap and
        return it as a dict.
        """

        data: Dict[str, Union[float, datetime, timedelta, int]] = {}

        # Note that because each element's attributes and text are returned as strings, we need to convert those strings
        # to the appropriate datatype (datetime, float, int, etc).

        start_time_str = lap.attrib['StartTime']
        data['start_time'] = dp.parse(start_time_str)

        distance_elem = lap.find('ns:DistanceMeters', self.__namespaces)
        if distance_elem is not None:
            data['distance'] = float(distance_elem.text)

        total_time_elem = lap.find('ns:TotalTimeSeconds', self.__namespaces)
        if total_time_elem is not None:
            data['total_time'] = timedelta(seconds=float(total_time_elem.text))

        max_speed_elem = lap.find('ns:MaximumSpeed', self.__namespaces)
        if max_speed_elem is not None:
            data['max_speed'] = float(max_speed_elem.text)

        max_hr_elem = lap.find('ns:MaximumHeartRateBpm', self.__namespaces)
        if max_hr_elem is not None:
            data['max_hr'] = float(max_hr_elem.find('ns:Value', self.__namespaces).text)

        avg_hr_elem = lap.find('ns:AverageHeartRateBpm', self.__namespaces)
        if avg_hr_elem is not None:
            data['avg_hr'] = float(avg_hr_elem.find('ns:Value', self.__namespaces).text)

        return data

    def __get_tcx_point_data(self, point: lxml.etree._Element) -> Optional[Dict[str, Union[float, int, str, datetime]]]:
        """Extract some data from an XML element representing a track point
        and return it as a dict.
        """

        data: Dict[str, Union[float, int, str, datetime]] = {}

        position = point.find('ns:Position', self.__namespaces)
        if position is None:
            # This Track-point element has no latitude or longitude data.
            # For simplicity's sake, we will ignore such points.
            return None
        else:
            data['latitude'] = float(position.find('ns:LatitudeDegrees', self.__namespaces).text)
            data['longitude'] = float(position.find('ns:LongitudeDegrees', self.__namespaces).text)

        time_str = point.find('ns:Time', self.__namespaces).text
        data['time'] = dp.parse(time_str)

        elevation_elem = point.find('ns:AltitudeMeters', self.__namespaces)
        if elevation_elem is not None:
            data['elevation'] = float(elevation_elem.text)

        hr_elem = point.find('ns:HeartRateBpm', self.__namespaces)
        if hr_elem is not None:
            data['heart_rate'] = int(hr_elem.find('ns:Value', self.__namespaces).text)

        cad_elem = point.find('ns:Cadence', self.__namespaces)
        if cad_elem is not None:
            data['cadence'] = int(cad_elem.text)

        # The ".//" here basically tells lxml to search recursively down the tree for the relevant tag, rather than
        # just the immediate child elements of speed_elem. See https://lxml.de/tutorial.html#elementpath
        speed_elem = point.find('.//ns3:Speed', self.__namespaces)
        if speed_elem is not None:
            data['speed'] = float(speed_elem.text)

        return data

    def __points_to_model_objs(self, df: pd.DataFrame) -> list:
        return [
            Point(
                user_id=self.entry.customer.id,
                entry_id=self.entry.id,
                latitude=row['latitude'],
                longitude=row['longitude'],
                lap_number=row['lap'],
                altitude=row['elevation'],
                timestamp=row['time'],
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
                total_distance=row['distance'],
                total_elapsed_time=row['total_time'].total_seconds(),
                max_speed=row['max_speed'],
                max_heart_rate=row['max_hr'],
                avg_heart_rate=row['avg_hr']
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
    def get_dataframe_from_file(self, file_path: str):
        """Get dataframe from file"""
        tree = lxml.etree.parse(file_path)
        root = tree.getroot()
        activity = root.find('ns:Activities', self.__namespaces)[
            0]  # Assuming we know there is only one Activity in the TCX file
        # (or we are only interested in the first one)
        points_data = []
        laps_data = []
        lap_no = 1
        for lap in activity.findall('ns:Lap', self.__namespaces):
            # Get data about the lap itself
            single_lap_data = self.__get_tcx_lap_data(lap)
            single_lap_data['number'] = lap_no
            laps_data.append(single_lap_data)

            # Get data about the track points in the lap
            track = lap.find('ns:Track', self.__namespaces)
            for point in track.findall('ns:Trackpoint', self.__namespaces):
                single_point_data = self.__get_tcx_point_data(point)
                if single_point_data:
                    single_point_data['lap'] = lap_no
                    points_data.append(single_point_data)
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
