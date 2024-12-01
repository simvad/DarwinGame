# Darwin Game Platform

A platform for running evolutionary game theory competitions where bots compete in a modified prisoner's dilemma game inspired by [The post by Zvi](https://www.lesswrong.com/s/GcZCMu7ZYHpJCh5bx/p/CnDsQAdzmDMF2LrY7)

## How It Works

Each game consists of multiple rounds where bots are randomly paired to play a sequence of turns. In each turn, both bots simultaneously choose a number between 0 and 5. If the sum is 5 or less, each bot earns points equal to their number. If the sum exceeds 5, neither bot gets points. A bot's success in each round determines how many copies of it survive to the next round.

### Features

- Create and manage multiple games
- Generate unique invite links for participants
- Secure bot submission and validation
- Real-time game visualization
- Support for various bot strategies

## Setup

1. Clone the repository and create a virtual environment:
```bash
git clone [repository-url]
cd darwin-game
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Create the admin account:
```bash
flask create-admin [username] [password]
```

4. Run the development server:
```bash
python run.py
```

## Running a Competition

### As Admin:

1. Login at http://localhost:5000 with your admin credentials
2. Create a new game with your desired settings
3. Generate invite links for participants
4. Share the links with participants
5. Start the game when all bots are submitted

### For Participants:

1. Receive invite link from admin
2. Click link to access bot submission page
3. Write your bot following the template provided
4. Submit your bot
5. Wait for the game to start to see results

## Bot Requirements

Bots must implement two methods:

```python
def get_move(self, history, opponent_history, round_number):
    # Must return an integer between 0 and 5
    return 2

def reset(self):
    # Called before each new game
    pass
```

Parameters:
- `history`: List of your previous moves
- `opponent_history`: List of opponent's previous moves
- `round_number`: Current round number (starting from 0)

## Production Deployment

For production use:

1. Set a secure secret key:
```python
# config.py
SECRET_KEY = 'your-secure-key-here'  # Use os.urandom(24).hex()
```

2. Use a production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 'app:create_app()'
```

3. Set up SSL/TLS if hosting publicly

## Security Notes

- Each invite link can only be used once
- Bot code is sandboxed and validated
- Limited to safe Python operations
- No file system or network access allowed
