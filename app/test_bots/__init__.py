import os

def load_test_bots():
    """Load all test bots from the test_bots directory."""
    bots = {}
    current_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            bot_name = filename[:-3].replace('_', ' ').title()  # Convert filename to nice name
            with open(os.path.join(current_dir, filename), 'r') as f:
                bot_code = f.read()
                bots[bot_name] = bot_code
                
    return bots
