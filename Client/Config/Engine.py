from dotenv import load_dotenv
import os

load_dotenv()

configClient    = {
    "IP":   os.getenv("IP"),
    "PORT": os.getenv("PORT"),
}

configServer       = {
    "IP":   os.getenv("IP_S"),
    "PORT": os.getenv("PORT_S"),
}