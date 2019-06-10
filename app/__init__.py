from flask import Flask
from config import Config
from  e2allpat import *
import zipfile
import zlib

app = Flask(__name__)
app.config.from_object(Config)

from app import routes
