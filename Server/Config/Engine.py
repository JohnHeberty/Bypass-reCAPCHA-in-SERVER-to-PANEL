from dotenv import load_dotenv
import os

load_dotenv()

configClient    = {
    "IP":       os.getenv("IP_C"),
    "PORT":     os.getenv("PORT_C"),
}

configServer       = {
    "IP":       os.getenv("IP"),
    "PORT":     os.getenv("PORT"),
    "URL":      os.getenv("URL"),
    "TIMEOUT":  os.getenv("PORT"),
    
}