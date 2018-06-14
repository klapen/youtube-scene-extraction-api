import os
from api import create_api

# Load configuration from enviromental variable
app = create_api(os.getenv('APP_SETTINGS'))

if __name__ == '__main__':
    app.run()
