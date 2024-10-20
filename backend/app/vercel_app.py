import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from backend.app.main import app

handler = Mangum(app)
