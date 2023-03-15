""" ASMR Intermediate Representation of Graphical Shapes

The shapes in this module can be translated into common graphical formats
such as SVG, DXF, KICAD_MOD, etc.
"""

import math

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
                 pattern='hatched',
                 cutoff='none',
                 group=None):
        # normalize color
        color = f'{color}FF' if len(color) == 7 else color

        # TODO DEBUG THIS
        # FINDING: THE OFFSET ANGLES ARE DIFFERENT FOR
        # TRIANGLES! NEED TO CALCULATE THE OFFSETS FOR TRIANGLES
        # AND USE APPROPRIATELY
        # THIS IS EXACTLY WHAT IS HAPPENING:
        # https://css-tricks.com/tight-fitting-svg-shapes/
        h = math.sqrt(2*(stroke_width**2))
        self.x0 = x0 + h #math.sqrt((stroke_width/2)**2)
        self.y0 = y0 + h #math.sqrt((stroke_width/2)**2) #stroke_width
        self.diagonal = diagonal - 2*h# 2*math.sqrt((stroke_width/2)**2) #- stroke_width
        self.x1 = self.x0 + self.diagonal/2 #-  math.sqrt((stroke_width**2)/2)
        self.y1 = self.y0 + self.diagonal/2
        self.x2 = self.x0
        self.y2 = self.y0 + self.diagonal #- stroke_width/2
        self.x3 = self.x0 - self.diagonal/2 # + stroke_width/2
        self.y3 = self.y0 + self.diagonal/2
        self.color = color if fill == 1 else f'{color[:-2]}00'
        self.fill = fill
        self.stroke_width = stroke_width
        self.pattern = pattern
        self.cutoff = cutoff
        self.group = group
        self.fill_lines = []

        self.apply_cutoff()
        self.generate_fill_lines()

    def apply_cutoff(self):
        if self.cutoff == 'none':
            return
        elif self.cutoff == 'top':
            self.x0 = self.x1
            self.y0 = self.y1
        elif self.cutoff == 'right':
            self.x1 = self.x2
            self.y1 = self.y2
        elif self.cutoff == 'bottom':
            self.x2 = self.x3
            self.y2 = self.y3
        elif self.cutoff == 'left':
            self.x3 = self.x0
            self.y3 = self.y0

    def generate_fill_lines(self):
        if self.fill == 1 or self.fill == 0:
            return

        # determine the number of lines per angle given the fill
        side_length = math.sqrt((self.diagonal**2)/2)
        n = math.floor((side_length / self.stroke_width) * self.fill)
        dh = side_length / n
        delta = math.sqrt((dh**2)/2)

        xstart = self.x0
        ystart = self.y0
        xend = self.x3
        yend = self.y3
        xstart_coef = 1
        xend_coef = 1
        ystart_coef = 1
        yend_coef = 1

        if self.pattern == 'hatched' or self.pattern == 'right':
            if self.cutoff == 'top':
                xstart = self.x3
                ystart = self.y3
                xstart_coef = 2
                ystart_coef = 0
            elif self.cutoff == 'right':
                xstart_coef = 0
                ystart_coef = 2
            elif self.cutoff == 'left':
                xend_coef = 0
                yend_coef = 2
            elif self.cutoff == 'bottom':
                xend_coef = 2
                yend_coef = 0

            for i in range(1, n):
                self.fill_lines.append(Line(
                    xstart_coef*i*delta + xstart,
                    ystart_coef*i*delta + ystart,
                    xend_coef*i*delta + xend,
                    yend_coef*i*delta + yend,
                    width=self.stroke_width,
                    color='#00FF00FF', #f'{self.color[:-2]}FF',
                    group=self.group
                ))
        if self.pattern == 'hatched' or self.pattern == 'left':
            xstart = self.x0
            ystart = self.y0
            xend = self.x1
            yend = self.y1
            xstart_coef = -1
            xend_coef = -1
            ystart_coef = 1
            yend_coef = 1

            if self.cutoff == 'top':
                xstart_coef = -2
                ystart_coef = 0
            elif self.cutoff == 'right':
                xend = self.x0
                yend = self.y0
                xend_coef = 0
                yend_coef = 2
            elif self.cutoff == 'left':
                xstart_coef = 0
                ystart_coef = 2
            elif self.cutoff == 'bottom':
                xend_coef = -2
                yend_coef = 0
            for i in range(1, n):
                self.fill_lines.append(Line(
                    xstart_coef*i*delta + xstart,
                    ystart_coef*i*delta + ystart,
                    xend_coef*i*delta + xend,
                    yend_coef*i*delta + yend,
                    width=self.stroke_width,
                    color=f'{self.color[:-2]}FF',
                    group=self.group
                ))



        # TODO make fill lines


class SVG:
    def __init__(self, filename, shapes=[]):
        self.filename = filename
        self.groups = {}
        self.scale = 3.543307 * 10
        self.dwg = svgwrite.drawing.Drawing(self.filename, profile='full')
        self.scale_group = self.dwg.g(transform=f'scale({self.scale})')
        self.dwg.add(self.scale_group)
        if len(shapes) > 0:
            self.from_shapes(shapes)

    def from_shapes(self, shapes):
        for shape in shapes:
            if shape.group not in self.groups and shape.group != None:
                self.groups[shape.group] = self.dwg.g(id=shape.group)
                self.scale_group.add(self.groups[shape.group])

            group = self.dwg if shape.group == None else self.groups[shape.group]
            c = SVG.convert_hex_color(shape.color)

            if shape.__class__ is Line:
                group.add(self.dwg.line(
                    (shape.x0, shape.y0),
                    (shape.x1, shape.y1),
                    stroke=c[0],
                    stroke_opacity=c[1],
                    stroke_width=shape.width,
                    stroke_linecap=shape.linecap
                ))
            if shape.__class__ is Rectangle:
                group.add(self.dwg.rect(
                    (shape.x0, shape.y0),
                    ((shape.x1-shape.x0), (shape.y1-shape.y0)),
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
                    fill='none' if shape.fill < 1 else c[0],
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
