from enum import Enum

import svgwrite
from svgwrite import mm

import asmr.kicad
from .gfx import Line


class GridPattern(Enum):
    Interleaved = 'interleaved'
    Diamond     = 'diamond'


class CapacitiveGrid:
    def __init__(self,
                 filename: str,
                 size=(1, 1),      # (X, Y)
                 pitch=5,          # width|height of button (mm)
                 xwidth=0.5,       # width of x electrode traces
                 ywidth=0.5,       # width of y electrode traces
                 separation=0.5,   # min separation between electrodes
                 use_color=False): # display different color electrodes
        isExtensionless = len(filename.split('.')) < 2 # TODO or check valid extensions
        self.fmt = 'svg' if isExtensionless else filename.split('.')[-1]
        self.filename = f'{filename}.{fmt}' if isExtensionless else filename
        self.size = size
        self.pitch = pitch
        self.xwidth = xwidth
        self.ywidth = ywidth
        self.separation = separation
        self.use_color = use_color
        self.gfx = []
        self.dwg = svgwrite.drawing.Drawing(self.filename, profile='full')

    def save(self):
        if (self.fmt == 'svg'):
            self.save_svg()
        elif self.fmt == "kicad_mod":
            self.save_kicad_footprint()

    def save_svg(self):
        dwg = svgwrite.drawing.Drawing(self.filename, profile='full')
        groups = {}
        for shape in self.gfx:
            if shape.group not in groups and shape.group != None:
                groups[shape.group] = dwg.g(id=shape.group)
                dwg.add(groups[shape.group])
            group = shape.group if shape.group == None else groups[shape.group]
            shape.to_svg(dwg, group=group)
        dwg.save()

    def save_kicad_footprint(self):
        asmr.kicad.render_footprint(grid.filename)


def create_interleaved_grid(grid: CapacitiveGrid):
    # calculate space between x-y electrodes from target separation
    ydigits_per_node = 0
    remaining_space = grid.pitch - grid.xwidth
    while remaining_space > (2*ydigits_per_node*grid.separation):
        ydigits_per_node += 1
        remaining_space = grid.pitch - ydigits_per_node*(grid.xwidth + grid.ywidth)
    ydigits_per_node -= 1
    remaining_space = grid.pitch - ydigits_per_node*(grid.xwidth + grid.ywidth)
    grid.separation = remaining_space / (2*ydigits_per_node)
    n_xdigits = (ydigits_per_node * grid.size[1]) + 1
    dy_xdigits = grid.separation*2 + grid.ywidth + grid.xwidth

    x_offset = grid.ywidth/2
    y_offset = grid.xwidth/2

    for column in range(grid.size[0]):
        group = f'column-{column}'

        # create X columns
        xcenter = column*grid.pitch + grid.pitch/2 + x_offset
        ylength = grid.pitch * grid.size[1]
        grid.gfx.append(Line(
            xcenter,
            y_offset,
            xcenter,
            ylength + y_offset,
            width=grid.xwidth,
            color='#0000FF' if grid.use_color else '#000000',
            group=group,
        ))

        # the minimum columnar digits (surrounding each node)
        min_x_digits = grid.size[1] + 1
        x_length = grid.pitch - grid.ywidth - (2*grid.separation) - grid.xwidth
        for digit in range(n_xdigits):
            x_start = xcenter - (x_length/2)
            x_end   = xcenter + (x_length/2)
            y = digit * dy_xdigits + y_offset
            grid.gfx.append(Line(
                x_start,
                y,
                x_end,
                y,
                width=grid.xwidth,
                color='#0000FF' if grid.use_color else '#000000',
                linecap='round',
                group=group,
            ))

    for row in range(grid.size[1]):
        group = f'row-{row}'

        y_start = row*grid.pitch + grid.xwidth + grid.separation + y_offset
        ylength = grid.pitch - grid.xwidth - grid.ywidth - grid.separation*2
        for column in range(grid.size[0] + 1):
            xcenter = column*grid.pitch + x_offset
            grid.gfx.append(Line(
                xcenter,
                y_start,
                xcenter,
                y_start+ylength,
                width=grid.ywidth,
                color='#FF0000' if grid.use_color else '#000000',
                group=group,
            ))
            for digit in range(ydigits_per_node):
                digit_y = y_start + digit*(grid.xwidth + 2*grid.separation + grid.ywidth)
                digit_length = None
                digit_x_start = None
                if column > 0 and column < (grid.size[0]):
                    digit_length = grid.pitch - grid.separation*2 - grid.xwidth - grid.ywidth
                    digit_x_start = xcenter - digit_length/2
                elif column == 0:
                    digit_x_start = xcenter
                    digit_length  = grid.pitch/2 - grid.xwidth/2 - grid.separation - grid.ywidth/2
                elif column == grid.size[0]:
                    digit_length  = -(grid.pitch/2 - grid.xwidth/2 - grid.separation - grid.ywidth/2)
                    digit_x_start = xcenter

                grid.gfx.append(Line(
                    digit_x_start,
                    digit_y,
                    digit_x_start + digit_length,
                    digit_y,
                    width=grid.ywidth,
                    color='#FF0000' if grid.use_color else '#000000',
                    linecap='round',
                    group=group,
                ))

def create_diamond_grid(grid: CapacitiveGrid):
    # TODO
    print(grid.xwidth)


class CapacitiveGridGenerator:
    def __init__(self,
                 size=(1, 1),
                 pitch=5,
                 xwidth=0.5,
                 ywidth=0.5,
                 separation=0.5,
                 use_color=False):
        self.size = (1, 1) if size is None else size
        self.pitch = 5.0 if pitch is None else pitch
        self.xwidth = 0.5 if xwidth is None else xwidth
        self.ywidth = 0.5 if ywidth is None else ywidth
        self.separation = 0.5 if separation is None else separation
        self.use_color = False if use_color is None else use_color

    def create(self, pattern: GridPattern, filename: str) -> CapacitiveGrid:
        grid = CapacitiveGrid(filename,
                              size = self.size,
                              pitch = self.pitch,
                              xwidth = self.xwidth,
                              ywidth = self.ywidth,
                              separation = self.separation,
                              use_color = self.use_color)
        if pattern is GridPattern.Interleaved:
            create_interleaved_grid(grid)
        elif pattern is GridPattern.Diamond:
            create_diamond_grid(grid)
        grid.save()
