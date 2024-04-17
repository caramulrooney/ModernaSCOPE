import json
from types import SimpleNamespace

class NullPathNode():
    def __init__(self, value):
        self._value = value

    def __getattr__(self, attr_name):
        return NullPathNode(self._value)

    def __bool__(self):
        return self._value

class debugPathNode():
    def __init__(self, name):
        self._name = name
        self._value = False
        self._children = {}

    def add_child(self, child_name: str):
        if child_name in self._children.keys():
            return
        # else:
        self._children[child_name] = debugPathNode(child_name)
        self.__dict__.update(self._children)

    def set_value(self, value):
        self._value = value

    def __bool__(self):
        return self._value

    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        # else:
        return NullPathNode(self._value)

class debugNamespace(debugPathNode):
    def __init__(self, json_file_name):
        super().__init__("debug")
        self.from_json(json_file_name)

    def from_json(self, json_file_name):
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
        print(debug_paths)

        print(sorted(debug_paths, key = lambda x: len(x[0])))

        # create debug namespace tree
        for debug_path, value in sorted(debug_paths, key = lambda x: len(x[0])):
            object_to_append_to = self
            for depth, child_name in enumerate(debug_path):
                object_to_append_to.add_child(child_name)
                object_to_append_to = object_to_append_to._children[child_name]
                if depth == len(debug_path) - 1:
                    object_to_append_to.set_value(value)
        self.__dict__.update(self._children)

my_debug = debugNamespace("C:/dev/git/ModernaSCOPE/Scope_Firmware/Python/pythonApi/dev_in_progress/debugConfig.json")

print("Hello World!")
print("Hello World!")
