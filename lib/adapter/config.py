import yaml


class Config:
    config = {}

    def __init__(self):
        with open('conf/main.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        if self.config['type'] not in ['client', 'server']:
            print('Invalid type in main.yaml, must be client or server')
            exit(1)
        elif self.config['type'] == 'client':
            self.config['mods_path'] = self.config['client_mods_path']
        elif self.config['type'] == 'server':
            self.config['mods_path'] = self.config['server_mods_path']

    def read(self):
        return self.config
