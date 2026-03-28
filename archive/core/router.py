from core import brain

def route_command(text):
    """
    Routes the user's command to the brain and returns the response.
    """
    reply, exit_flag = brain.think(text)
    return reply, exit_flag
