import yaml


class Config:
    config = {}

    def __init__(self):
        with open('conf/main.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

    def read(self):
        return self.config
