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

    def to_svg(self,
               dwg,
               group=None):
        if group == None:
            group = dwg

        group.add(dwg.line(
            (self.x0*mm, self.y0*mm),
            (self.x1*mm, self.y1*mm),
            stroke=self.color,
            stroke_width=self.width*mm,
            stroke_linecap=self.linecap
        ))
