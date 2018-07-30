
from mkdocs.plugins import BasePlugin

class MkdocsPlugin(BasePlugin):
    def on_config(self, config, **kwargs):
        #config['theme'].static_templates.add('my_template.html')
        #print(config)
        return config
