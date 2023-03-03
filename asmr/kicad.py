""" AMSR KiCAD Tools"""

import os
from pathlib import Path

import jinja2

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
FOOTPRINT_EXT = 'kicad_mod'
FOOTPRINT_TEMPLATE = Path(f'{DIR_PATH}/templates/footprint.{FOOTPRINT_EXT}.jinja')

def render_template(output_filename, template, context):
    with open(template, 'r') as fd:
        t = jinja2.Template(fd.read())
    t.stream(**context).dump(str(Path.cwd()/output_filename))

def render_footprint(footprint_name):
    if footprint_name.split('.')[-1] != FOOTPRINT_EXT:
        footprint_name = f'{footprint_name}.{FOOTPRINT_EXT}'

    ctx = {
        'footprint_name': f'"{footprint_name}"',
        'date_created': '20230303',
        'generating_program': 'asmr'
    }
    render_template(footprint_name, FOOTPRINT_TEMPLATE, ctx)
