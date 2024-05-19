import os 


def load_compiled_module_if_exists(self, module_name: str):
    directory_path = "/my_vol/compiled_modules/"

    if os.path.exists(directory_path + module_name + ".json"):
        self.load(os.path.join(directory_path, module_name + ".json"))
        print("Compiled Module Loaded: ", module_name)
        return None

    print("Compiled Module Not Found: ", module_name)
    return None
