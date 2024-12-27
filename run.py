from app import create_app
import sys

# Get configuration from command line argument
config_name = sys.argv[1] if len(sys.argv) > 1 else 'production'
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)
