#

from ilot.core.manager import AppManager


actions = AppManager.get_actions()

for action in actions:

    # evaluate the action tag function
    action_tag = """
    import {{className}}

    def action_name(item, param_a=None, param_b=None):

        action = {{action}}
        # execute the action within the context

        return rendered_content
    """
    # register it
