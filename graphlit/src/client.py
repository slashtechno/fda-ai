from dotenv import load_dotenv
import os

from graphlit import Graphlit
from graphlit_api import input_types, enums, exceptions

load_dotenv()


graphlit = Graphlit(
    organization_id=os.environ.get('GRAPHLIT_ORGANIZATION_ID'),
    environment_id=os.environ.get('GRAPHLIT_ENVIRONMENT_ID'),
    jwt_secret=os.environ.get('GRAPHLIT_JWT_SECRET')
)

if graphlit is None:
    raise Exception("Failed to initialize Graphlit client")