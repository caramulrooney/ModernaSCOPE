import datetime as dt
from pytz import timezone
import operator

class CalibrationDatum():
    def __init__(self, ph, voltage, timestamp):
        self.ph = ph
        self.voltage = voltage
        self.timestamp = timestamp
        self.is_recent = True

    def __repr__(self):
        return f"{{ph: {self.ph}, voltage: {self.voltage}, timestamp: {self.timestamp}}}" # TODO: jsonify timestamp

class CalibrationHistory():
    my_tz = timezone('US/Eastern')
    max_calibration_time = dt.timedelta(hours = 12)
    calibration_data = []
    recent_calibration_data = []
    def __init__(self, electrode_id):
        self.electrode_id = electrode_id

    def add_calibration(self, ph, voltage):
        self.calibration_data.append(CalibrationDatum(ph, voltage, dt.datetime.now(self.my_tz)))

    def mark_old_calibrations(self, epsilon = 0.5):
        time_sorted_data = sorted(self.calibration_data, key = operator.attrgetter('timestamp'), reverse = True) # sort from most recent to least recent

        for time_sorted_datum in time_sorted_data:
            if dt.datetime.now(self.my_tz) - time_sorted_datum.timestamp > self.max_calibration_time:
                time_sorted_datum.is_recent = False
            if not time_sorted_datum.is_recent:
                continue
            # compare other data points to the current most recent data point
            for datum in self.calibration_data:
                if datum.timestamp < time_sorted_datum.timestamp and abs(datum.ph - time_sorted_datum.ph) < epsilon:
                    datum.is_recent = False

    def get_recent_calibrations(self):
        self.mark_old_calibrations(epsilon = 0.5)
        recent_calibrations = []
        for datum in self.calibration_data:
            if datum.is_recent:
                recent_calibrations.append(datum)
        self.recent_calibration_data = recent_calibrations
        return recent_calibrations
