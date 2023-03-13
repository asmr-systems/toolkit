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

class Rectangle:
    def __init__(self,
                 x0,
                 y0,
                 x1,
                 y1,
                 width=0.5,
                 fill=True,
                 color='#000000',
                 rx=0,
                 ry=0,
                 group=None):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.fill = fill
        self.color = color
        self.rx = rx
        self.ry = ry
        self.group = group

class Diamond:
    def __init__(self,
                 x0,
                 y0,
                 diagonal,
                 fill = 1.0, # fill between 0 and 1
                 color='#000000FF',
                 stroke_width=0,
                 group=None):
        # normalize color
        color = f'{color}FF' if len(color) == 7 else color

        # TODO WORK ON THIS TO GET THE STROKE OFFSET CORRECT!
        self.x0 = x0
        self.y0 = y0 + stroke_width/2
        self.diagonal = diagonal - stroke_width
        self.x1 = self.x0 + self.diagonal/2 - stroke_width/2
        self.y1 = self.y0 + self.diagonal/2
        self.x2 = self.x0
        self.y2 = self.y0 + self.diagonal - stroke_width/2
        self.x3 = self.x0 - self.diagonal/2 + stroke_width/2
        self.y3 = self.y0 + self.diagonal/2
        self.color = color if fill == 1 else f'{color[:-2]}00'
        self.fill = fill
        self.stroke_width = stroke_width
        self.group = group
        self.fill_lines = []

        self.generate_fill_lines()

    def generate_fill_lines(self):
        if self.fill == 1:
            return

        # TODO make fill lines


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
            c = SVG.convert_hex_color(shape.color)

            if shape.__class__ is Line:
                group.add(self.dwg.line(
                    (shape.x0*mm, shape.y0*mm),
                    (shape.x1*mm, shape.y1*mm),
                    stroke=c[0],
                    stroke_opacity=c[1],
                    stroke_width=shape.width*mm,
                    stroke_linecap=shape.linecap
                ))
            if shape.__class__ is Rectangle:
                group.add(self.dwg.rect(
                    (shape.x0*mm, shape.y0*mm),
                    ((shape.x1-shape.x0)*mm, (shape.y1-shape.y0)*mm),
                    rx=shape.rx,
                    ry=shape.ry,
                    fill=c[0],
                    opacity=c[1],
                    stroke_width=0,
                ))
            if shape.__class__ is Diamond:
                group.add(self.dwg.polygon(
                    [(shape.x0, shape.y0),
                     (shape.x1, shape.y1),
                     (shape.x2, shape.y2),
                     (shape.x3, shape.y3)],
                    fill='none' if shape.fill < 1 else c[0], #c[0],
                    stroke=c[0],
                    stroke_width=shape.stroke_width,
                ))
                self.from_shapes(shape.fill_lines)

    @staticmethod
    def convert_hex_color(hexc):
        """ returns a 2-tuple (rgb_hex_color, alpha_percent)"""
        if (len(hexc) == 7):
            return (hexc, '1.0')
        return (hexc[:-2], f'{(int(hexc[-2:], 16)/255):.2f}')

    def save(self):
        self.dwg.save()
