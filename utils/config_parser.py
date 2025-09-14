import os

class Config:
    def __init__(self, filepath):
        self.filepath = filepath
        self.options = {}
        self._parse()

    def _parse(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Config file not found: {self.filepath}")

        with open(self.filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                self.options[key.strip()] = value.strip()

    def get(self, key, default=None):
        return self.options.get(key, default)

    def __getitem__(self, key):
        return self.options[key]

    def __repr__(self):
        return f"<Config {self.filepath}: {self.options}>"
