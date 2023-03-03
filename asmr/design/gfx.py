""" ASMR Intermediate Representation of Graphical Shapes

The shapes in this module can be translated into common graphical formats
such as SVG, DXF, KICAD_MOD, etc.
"""

import svgwrite
from svgwrite import mm


class Line:
    def __init__(self,
                 x0,
                 y0,
                 x1,
                 y1,
                 width=0.5,
                 color='#000000',
                 linecap='butt',
                 group=None):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.color = color
        self.linecap = linecap
        self.group = group


class SVG:
    def __init__(self, filename, shapes=[]):
        self.filename = filename
        self.groups = {}
        self.dwg = svgwrite.drawing.Drawing(self.filename, profile='full')
        if len(shapes) > 0:
            self.from_shapes(shapes)

    def from_shapes(self, shapes):
        for shape in shapes:
            if shape.group not in self.groups and shape.group != None:
                self.groups[shape.group] = self.dwg.g(id=shape.group)
                self.dwg.add(self.groups[shape.group])

            group = self.dwg if shape.group == None else self.groups[shape.group]

            if shape.__class__ is Line:
                group.add(self.dwg.line(
                    (shape.x0*mm, shape.y0*mm),
                    (shape.x1*mm, shape.y1*mm),
                    stroke=shape.color,
                    stroke_width=shape.width*mm,
                    stroke_linecap=shape.linecap
                ))

    def save(self):
        self.dwg.save()
