#!/usr/bin/python
from wsgiref.handlers import CGIHandler
from jllPortal import app

CGIHandler().run(app)