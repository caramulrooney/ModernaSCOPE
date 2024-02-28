from functools import total_ordering
import inspect
import datetime as dt
from pytz import timezone
import operator

@total_ordering
class CalibrationDatum():
    def __init__(self, ph, voltage, timestamp):
        self.ph = ph
        self.voltage = voltage
        self.timestamp = timestamp
        self.is_recent = True

    def to_json(self):
        return f"{{ph: {self.ph}, voltage: {self.voltage}, timestamp = {self.timestamp}}}" # TODO: jsonify timestamp

class Calibration():
    my_tz = timezone('US/Eastern')
    max_calibration_time = dt.timedelta(hours = 12)
    calibration_data = []
    recent_calibration_data = []
    def __init__(self, electrode_id):
        self.electrode_id = electrode_id

    def add_calibration(self, ph, voltage):
        self.calibration_data.append(CalibrationDatum(ph, voltage, dt.now(self.my_tz)))

    def mark_old_calibrations(self, epsilon = 0.5):
        time_sorted_data = sorted(self.calibration_data, key = operator.attrgetter('timestamp'), reverse = True) # sort from most recent to least recent

        for time_sorted_datum in time_sorted_data:
            if dt.now(self.my_tz) - time_sorted_datum.timestamp > self.max_calibration_time:
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


class Sensor():
    def unpack_namespace(func):
        def inner(self, namespace):
            sig = inspect.signature(func)
            kwargs = vars(namespace)
            kwargs["self"] = self
            args_to_pass = [kwargs[arg] for arg in sig.parameters.keys()]
            func(*args_to_pass)
        return inner

    @unpack_namespace
    def measure(self, electrodes, now, time_steps, max_time, voltage_only):
        print(f"Inside of measure, {electrodes=}, {now=}, {time_steps=}, {max_time=}, {voltage_only=}")

    @unpack_namespace
    def calibrate(self, electrodes, ph):
        print(f"Inside of calibrate, {electrodes=}, {ph=}")

    @unpack_namespace
    def show_calibration(self, electrodes, ph, sort_by_ph):
        print(f"Inside of calibrate, {electrodes=}, {ph=}, {sort_by_ph=}")

    @unpack_namespace
    def clear_calibration(self, electrodes, ph, all):
        print(f"Inside of calibrate, {electrodes=}, {ph=}, {all=}")
