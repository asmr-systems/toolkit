""" AMSR KiCAD Tools"""

import os
import uuid
from pathlib import Path

import jinja2

import asmr.design.gfx


DIR_PATH = os.path.dirname(os.path.realpath(__file__))
FOOTPRINT_EXT = 'kicad_mod'
FOOTPRINT_TEMPLATE = Path(f'{DIR_PATH}/templates/footprint.{FOOTPRINT_EXT}.jinja')

def render_template(output_filename, template, context):
    with open(template, 'r') as fd:
        t = jinja2.Template(fd.read())
    t.stream(**context).dump(str(Path.cwd()/output_filename))

class Line:
    def __init__(self,
                 x0,
                 y0,
                 x1,
                 y1,
                 width,
                 layer="F.SilkS"):
        self.uuid = uuid.uuid4()
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.layer = layer

    @staticmethod
    def from_gfx(line, layer="F.SilkS", offset=(0, 0)):
        return Line(
            line.x0 - offset[0],
            line.y0 - offset[1],
            line.x1 - offset[0],
            line.y1 - offset[1],
            line.width,
            layer=layer,
        )

class Rectangle:
    def __init__(self,
                 x0,
                 y0,
                 x1,
                 y1,
                 width=0,
                 layer="F.SilkS"):
        self.uuid = uuid.uuid4()
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.layer = layer

    @staticmethod
    def from_gfx(line, layer="F.SilkS", offset=(0, 0)):
        return Rectangle(
            line.x0 - offset[0],
            line.y0 - offset[1],
            line.x1 - offset[0],
            line.y1 - offset[1],
            # line.width,
            layer=layer,
        )

class Diamond:
    def __init__(self,
                 x0,
                 y0,
                 x1,
                 y1,
                 x2,
                 y2,
                 x3,
                 y3,
                 width=0,
                 fill='none',
                 fill_lines=[],
                 layer='F.Cu',):
        self.uuid = uuid.uuid4()
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.width = width
        self.fill = fill
        self.fill_lines=[]
        self.layer=layer

    @staticmethod
    def from_gfx(diamond, layer="F.Cu", offset=(0, 0)):
        return Diamond(
            diamond.x0 - offset[0],
            diamond.y0 - offset[1],
            diamond.x1 - offset[0],
            diamond.y1 - offset[1],
            diamond.x2 - offset[0],
            diamond.y2 - offset[1],
            diamond.x3 - offset[0],
            diamond.y3 - offset[1],
            width=diamond.stroke_width,
            fill = 'solid' if diamond.fill == 1.0 else 'none',
            fill_lines=diamond.fill_lines,
            layer=layer,
        )

class FpPad:
    def __init__(self, id):
        self.id = id
        self.uuid = uuid.uuid4()
        self.type = 'smd'
        self.shape = 'custom'
        self.lines = []
        self.diamonds = []
        self.x = 0
        self.y = 0

    def set_origin(self, x, y):
        if (len(self.lines) == 0 and len(self.diamonds) == 0):
            self.x = x
            self.y = y

    def add_line(self, line):
        self.set_origin(line.x0, line.y0)
        self.lines.append(Line.from_gfx(line, layer="F.Cu", offset=(self.x, self.y)))
        self.width = self.lines[-1].width

    def add_diamond(self, diamond):
        self.set_origin(diamond.x0, diamond.y0)
        self.diamonds.append(Diamond.from_gfx(diamond, layer="F.Cu", offset=(self.x, self.y)))
        if len(diamond.fill_lines) != 0:
            for line in diamond.fill_lines:
                self.lines.append(
                    Line.from_gfx(line,
                                  layer="F.Cu",
                                  offset=(self.x, self.y))
                )
        self.width = self.diamonds[-1].width

class Footprint:
    def __init__(self,
                 filename,
                 pads=[],
                 mask=[],
                 silkscreen=[]):
        self.filename = filename
        self.pads = {}
        self.mask = {'rects': []}
        self.silkscreen = {'lines': []}
        if len(pads) > 0:
            self.pads_from_shapes(pads)
        if len(mask) > 0:
            self.mask_from_shapes(mask)
        if len(silkscreen) > 0:
            self.silkscreen_from_shapes(silkscreen)

    def pads_from_shapes(self, shapes):
        for shape in shapes:
            pad_id = shape.group.split("=")[-1]

            if pad_id in self.pads:
                pad = self.pads[pad_id]
            else:
                pad = FpPad(pad_id)
                self.pads[pad_id] = pad

            if shape.__class__ == asmr.design.gfx.Line:
                pad.add_line(shape)
            elif shape.__class__ == asmr.design.gfx.Diamond:
                pad.add_diamond(shape)


    def mask_from_shapes(self, shapes):
        for shape in shapes:
            if shape.__class__ == asmr.design.gfx.Rectangle:
                self.mask['rects'].append(Rectangle.from_gfx(shape, layer="F.Mask"))

    def silkscreen_from_shapes(self, shapes):
        for shape in shapes:
            if shape.__class__ == asmr.design.gfx.Line:
                self.silkscreen['lines'].append(Line.from_gfx(shape, layer="F.SilkS"))

    def save(self):
        name = '.'.join(self.filename.split('.')[:-1])
        ctx = {
            'footprint_name': f'{name}',
            'date_created': '20230303',
            'generating_program': 'asmr',
            'description': 'a footprint generated by asmr toolkit.',
            'canonical_layer': 'F.Cu',
            'fp_type': 'smd',
            'pads': self.pads.values(),
            'silkscreen': self.silkscreen,
            'mask': self.mask,
        }
        render_template(self.filename, FOOTPRINT_TEMPLATE, ctx)
