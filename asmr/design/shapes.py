""" ASMR Intermediate Representation of Graphical Shapes

The shapes in this module can be translated into common graphical formats
such as SVG, DXF, KICAD_MOD, etc.
"""


class Line:
    def __init__(self,
                 x0,
                 y0,
                 x1,
                 y1,
                 width=0.5,
                 group='all'):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.group = group

    def to_svg():
        pass
