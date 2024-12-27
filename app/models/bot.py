import ast
import inspect
from typing import Callable, List, Set
from concurrent.futures import ThreadPoolExecutor, TimeoutError

class BotValidator:
    ALLOWED_BUILTINS = {
        'range', 'len', 'int', 'float', 'list', 'tuple', 'dict', 
        'set', 'sum', 'min', 'max', 'sorted', 'round', 'abs',
        'all', 'any', 'enumerate', 'zip', 'map', 'filter'
    }
    
    MAX_SOURCE_LENGTH = 1500  # Allowed number of characters
    MAX_EXECUTION_TIME = 0.1  # Allowed seconds per move
    
    def __init__(self):
        self.violations = []
    
    def validate_source(self, source_code: str) -> bool:
        """Validates bot source code for security and compliance."""
        if len(source_code) > self.MAX_SOURCE_LENGTH:
            self.violations.append(
                f"Code is too long! Maximum allowed length is {self.MAX_SOURCE_LENGTH} characters. "
                f"Your code is {len(source_code)} characters."
            )
            return False
            
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            self.violations.append(
                f"Your code has a syntax error: {str(e)}. "
                "Please check that all parentheses, brackets, and quotes are properly closed."
            )
            return False
            
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self, validator):
                self.validator = validator
                self.found_violations = []
                
            def visit_Import(self, node):
                modules = [name.name for name in node.names]
                if not all(module == 'random' for module in modules):
                    not_allowed = [m for m in modules if m != 'random']
                    self.found_violations.append(
                        f"Only the 'random' module is allowed for security reasons. "
                        f"Attempted to import: {', '.join(not_allowed)}. "
                        f"You can only use the random module and these built-in functions: {', '.join(sorted(BotValidator.ALLOWED_BUILTINS))}"
                    )
                
            def visit_ImportFrom(self, node):
                if node.module != 'random':
                    self.found_violations.append(
                        f"Only imports from the 'random' module are allowed. "
                        f"Attempted to import from module '{node.module}'. "
                        f"You can only use the random module and these built-in functions: {', '.join(sorted(BotValidator.ALLOWED_BUILTINS))}"
                    )
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in BotValidator.ALLOWED_BUILTINS:
                        self.found_violations.append(
                            f"Function '{node.func.id}' is not allowed for security reasons. "
                            f"Allowed functions are: {', '.join(sorted(BotValidator.ALLOWED_BUILTINS))}"
                        )
                self.generic_visit(node)
                
        visitor = SecurityVisitor(self)
        visitor.visit(tree)
        
        if visitor.found_violations:
            self.violations.extend(visitor.found_violations)
            return False
            
        return True
    
    def validate_bot_class(self, bot_class: type) -> bool:
        """Validates that a bot class implements the required interface."""
        required_methods = {'get_move', 'reset'}
        
        # Check for required methods
        missing_methods = required_methods - set(dir(bot_class))
        if missing_methods:
            self.violations.append(
                f"Your bot is missing required methods: {', '.join(missing_methods)}. "
                "Your bot class must implement both 'get_move' and 'reset' methods."
            )
            return False
            
        # Validate get_move signature
        get_move = getattr(bot_class, 'get_move', None)
        if not callable(get_move):
            self.violations.append(
                "'get_move' must be a method that can be called. "
                "Make sure you defined it as 'def get_move(self, history, opponent_history, round_number):'"
            )
            return False
            
        sig = inspect.signature(get_move)
        params = list(sig.parameters.keys())
        
        # Remove 'self' from the parameter count if it's there
        if params and params[0] == 'self':
            params.pop(0)
            
        if len(params) != 3:
            self.violations.append(
                "get_move must accept exactly 3 parameters: history, opponent_history, and round_number. "
                f"Your method has {len(params)} parameters: {', '.join(params)}. "
                "The correct signature is: def get_move(self, history, opponent_history, round_number)"
            )
            return False
            
        return True
    
    def create_safe_environment(self) -> dict:
        """Creates a restricted environment for bot execution."""
        safe_env = {}
        safe_env['__builtins__'] = {
            name: __builtins__[name] 
            for name in self.ALLOWED_BUILTINS
            if name in __builtins__
        }
        # Add necessary builtin functions and variables for class definition
        required_builtins = {
            '__build_class__',  # Required for 'class' keyword
            '__name__',         # Required for class definition
            '__doc__',         # Sometimes used in class definition
            'None',            # Required for default values and comparisons
            'True',            # Required for boolean operations
            'False',           # Required for boolean operations
            '__import__'       # Required for importing modules
        }
        for name in required_builtins:
            safe_env['__builtins__'][name] = __builtins__[name]
        
        # Add __name__ at the module level as well
        safe_env['__name__'] = '__main__'
        
        # Add random module
        import random
        safe_env['random'] = random
        
        return safe_env

class BotRunner:
    def __init__(self, bot_class):
        self.bot = bot_class()
        self.history = []
        self.opponent_history = []
        
    def execute_move(self, round_number: int, opponent_last_move: int = None) -> int:
        """Executes a single move with timeout and validation."""
        if opponent_last_move is not None:
            self.opponent_history.append(opponent_last_move)
            
        def run_move():
            try:
                move = self.bot.get_move(
                    self.history.copy(),
                    self.opponent_history.copy(),
                    round_number
                )
            except TypeError as e:
                if "missing" in str(e):
                    raise ValueError(
                        "Your get_move method is missing parameters. "
                        "It must accept: self, history, opponent_history, round_number"
                    )
                elif "takes" in str(e):
                    raise ValueError(
                        "Your get_move method has too many parameters. "
                        "It must accept exactly: self, history, opponent_history, round_number"
                    )
                else:
                    raise ValueError(f"Type error in get_move: {str(e)}")
            
            if move is None:
                raise ValueError("get_move returned None instead of a number")
                
            if not isinstance(move, (int, float)):
                raise ValueError(
                    f"get_move must return a number, but returned {type(move).__name__}"
                )
                
            move = int(move)
            if not (0 <= move <= 5):
                raise ValueError(
                    f"get_move returned {move}, but must return a number between 0 and 5"
                )
                
            return move
            
        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                future = executor.submit(run_move)
                move = future.result(timeout=BotValidator.MAX_EXECUTION_TIME)
                self.history.append(move)
                return move
            except TimeoutError:
                raise RuntimeError("Bot exceeded maximum execution time")
            except Exception as e:
                raise RuntimeError(f"Bot execution failed: {str(e)}")
                
    def reset(self):
        """Resets the bot and clears history."""
        self.history = []
        self.opponent_history = []
        self.bot.reset()
