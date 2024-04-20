import json
from pathlib import Path
from types import SimpleNamespace

class Config():
    """
    Configuration information that may need to be changed by the user, such as file paths to measurement and calibration data. Properties defined in this class are distinct from those defined in constants.py in that they might need to change from one session to the next. All properties and methods belong to the class and can be accessed without instantiation.

    Load the config parameters and debug message options from a json file with set_config().

    If necessary, use make_directories() to initialize the folder structure so the data files can be created at runtime.
    """
    default_values = {
        "serial_port": "COM4",
        "measurement_interval": 1, # second
        "voltage_display_filename": "display/voltage_display.txt",
        "calibration_data_filename": "sensor_data/calibration_data.csv",
        "measurement_data_filename": "sensor_data/measurement_data.csv",
        "ph_result_filename": "sensor_data/ph_result.csv",
        "calibration_map_folder": "sensor_data/calibration_map/",
        "prompt_history_filename": "settings/prompt_history.txt",
        "timezone": "US/Eastern",
        "random_data": True,
    }
    debug = False

    @classmethod
    def set_config(cls, config_filename: str, debug_filename: str, mkdirs: bool) -> bool:
        """
        Read in configuration parameters as a json file and store the relevant fields as class properties. If a field is not provided, the default value is kept. Additional fields are ignored.

        `calibration_data_filename`: File in which to store calibration records.

        `measurement_data_filename`: File in which to store measurement records.

        `ph_result_filename`: File in which to store the results of pH conversion when a measurement is performed.

        `calibration_map_folder`: Directory in which to generate a new calibration map file for each measurement that is performed, to indicate which calibration data were used in the conversion of that measurement.

        `prompt_history_filename`: File in which to store the command line session history, so that previous commands can be accessed with the up arrow even if the terminal is closed and then re-opened.

        `timezone`: Time zone in which to store calibration and measurement records.
        """

        # initialize parameters with defaults
        for key, value in cls.default_values.items():
            setattr(cls, key, value)

        try:
            f = open(config_filename)
        except FileNotFoundError:
            print(f"Could not open file '{config_filename}'. Using default configuration settings instead.")
            return False

        # initialize parameters again with values from the json file, overwriting defaults as necessary
        data = json.load(f)
        for key, value in data.items():
            setattr(cls, key, value)

        cls.debug = DebugOptRoot(debug_filename)

        if mkdirs:
            cls.make_directories()
        return True

    @classmethod
    def make_directories(cls):
        """
        Initialize the folder structure required by the file paths so the files can be created at runtime.
        """
        Path(cls.calibration_map_folder).mkdir(parents = True, exist_ok = True)
        for path in [cls.calibration_data_filename, cls.measurement_data_filename, cls.ph_result_filename, cls.prompt_history_filename, cls.voltage_display_filename]:
            Path(path).parent.mkdir(parents = True, exist_ok = True)

class DebugOptLeaf():
    """
    Debug option tree leaf node. This node is created as the default child of any node when a child node does not exist. When any attribute is queried using dot notation or `__getaddr__()`, this will return a copy of itself. Any children of this class will have the same value as this class. This behavior allows the propagation of a node's attributes to all its children, even if those nodes are not explicitly defined. Thus, the following two caes produce exactly the same behavior.:
    ```
    if Config.debug.a.b:                if Config.debug.a.b.c.d.e.f:
        print(error_message)                print(error_message)
    ```
    An arbitrarily long chain of dot-indexing can be added without throwing any errors. This allows the developer to write debug messages which can be turned on and off with arbitrary specificity without having to include a comprehensive list of granular debug flags.
    """
    def __init__(self, value):
        self._value = value

    def __getattr__(self, attr_name):
        """
        When accessed with dot indexing, return a copy of itself, passing on the same value (True or False) to the child.
        """
        return DebugOptLeaf(self._value)

    def __bool__(self):
        """
        When evaluated inside an if statement, return True or False.
        """
        return self._value

class DebugOptNode():
    """
    Debug option tree node. Each node keeps track of its children and its current value, which it will return when queried with `__bool__()` inside of an `if` statement. When indexed using dot notation, it will first look in its dictionary of children, and if no such child exists, it will return a leaf node which will copy its value to every node below it in the hierarchy.
    """
    def __init__(self, name):
        self._name = name
        self._value = False
        self._children = {}

    def add_child(self, child_name: str):
        """
        Append a child node to the dictionary of children.
        """
        if child_name in self._children.keys():
            return
        # else:
        self._children[child_name] = DebugOptNode(child_name)
        self.__dict__.update(self._children)

    def set_value(self, value):
        """
        Set the value of this node (True or False) and all nodes beneath it in the hiearchy, unless those nodes are explicitly overwritten.
        """
        self._value = value

    def __bool__(self):
        """
        When evaluated inside an if statement, return True or False.
        """
        return self._value

    def __getattr__(self, key):
        """
        When indexed using dot notation, first look in the dictionary of children, and if no such child exists, return a leaf node which will copy its value to every node below it in the hierarchy.
        """
        if key in self.__dict__.keys():
            return self.__dict__[key]
        # else:
        return DebugOptLeaf(self._value)

class DebugOptRoot(DebugOptNode):
    """
    Debug option tree root node.

    The debug option tree is a data structure for efficiently filtering the printing of debug messages. This solves the problem of leaving debug if statements throughout the code like the following.
    ```
    if Config.debug:
        print(debug_message)
    ```
    If Config.debug is a global variable, then setting it to True turns on debug messages globally throughout every file, which will print an overwhelming number of debug messages and render each of them useless.

    Each node in this class and its subclasses implements the __bool__() function which will be evaluated inside an if statement. With this class, the debug print statement can be re-written as the following.
    ```
    if Config.debug.my.more.specific.debug.message:
        print(debug_message)
    ```
    Then, more specific debug flags can be included in the Config object so that only the most relevant messages are printed out.

    ---

    The debug option tree is a tree-like data structure, where the child nodes inherit from the parent nodes but can be overwritten. For example, if `Config.debug.a.b` is set to `True`, then `Config.debug.a.b.c` will also be set to `True` unless it is specifically overridden. Perhaps the nicest thing about using this data structure (instead of, say, a dictionary) is that not all nodes need to be defined in the top-level Config file. The developer can add debug messages inside of arbitrarily specific `if` statements, and the top-level Config file can simply include a more general class or error messages, or it can include or disinclude up to very specific subsets of debug messages. For the greatest granularity, it is recommended that every single debug message check on a unique debug tree option.
    """
    def __init__(self, json_file_name: str):
        super().__init__("debug")
        self.from_json(json_file_name)

    def from_json(self, json_file_name: str):
        """
        Generate a debug option tree from a given json file with this object as its root. The json file should be structured as follows, with dots (`.`) between each layer of hierarchy. Only the nodes of interest need to be defined; by default, each node will inherit the value of its parent, with the root node being `False`.

        Example:
        ```json
        {
            "cli": false,
            "cli.read_command": true,
            "cli.read_command.parse_electrode": false
        }
        ```
        """
        # read json file
        try:
            json_file = open(json_file_name)
        except FileNotFoundError:
            print(f"Could not open file '{json_file_name}'.")
            return False

        # check values in json file to make sure they're all bools
        data = json.load(json_file)
        for val in data.values():
            assert isinstance(val, bool)

        # split apart debug paths
        debug_paths = []
        for key, value in data.items():
            debug_paths.append((key.split("."), value))

        # create debug namespace tree
        # assign node values in most general to least general order, such that more specific values overwrite more general values in the hierarchy.
        for debug_path, value in sorted(debug_paths, key = lambda x: len(x[0])):
            object_to_append_to = self
            for depth, child_name in enumerate(debug_path):
                object_to_append_to.add_child(child_name)
                object_to_append_to = object_to_append_to._children[child_name]
                if depth == len(debug_path) - 1:
                    object_to_append_to.set_value(value)
        self.__dict__.update(self._children)
