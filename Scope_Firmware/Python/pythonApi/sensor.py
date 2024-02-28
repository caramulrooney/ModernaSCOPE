import inspect

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
