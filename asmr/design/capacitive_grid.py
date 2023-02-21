from enum import Enum

import svgwrite
from svgwrite import mm


class GridPattern(Enum):
    Interleaved = 'interleaved'
    Diamond     = 'diamond'


class CapacitiveGrid:
    def __init__(self,
                 filename: str,
                 size=(1, 1),     # (X, Y)
                 pitch=5,         # width|height of button (mm)
                 xwidth=0.5,      # width of x electrode traces
                 ywidth=0.5,      # width of y electrode traces
                 separation=0.5): # min separation between electrodes
        self.filename = filename
        self.size = size
        self.pitch = pitch
        self.xwidth = xwidth
        self.ywidth = ywidth
        self.separation = separation
        self.dwg = svgwrite.drawing.Drawing(self.filename, profile='full')

    def save(self):
        self.dwg.save()


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
    xdigits = (ydigits_per_node * grid.size[1]) + 1

    for column in range(grid.size[0]):
        # create X columns
        xcenter = column*grid.pitch + grid.pitch/2
        ylength = grid.pitch * grid.size[1]
        grid.dwg.add(grid.dwg.line(
            (xcenter*mm, 0),
            (xcenter*mm, ylength*mm),
            stroke=svgwrite.rgb(0,0,0),
            stroke_width=grid.xwidth*mm
        ))

        # the minimum columnar digits (surrounding each node)
        min_x_digits = grid.size[1] + 1

    #
    print(grid.size)


def create_diamond_grid(grid: CapacitiveGrid):
    # TODO
    print(grid.xwidth)


class CapacitiveGridGenerator:
    def __init__(self,
                 size=(1, 1),
                 pitch=5,
                 xwidth=0.5,
                 ywidth=0.5,
                 separation=0.5):
        self.size = (1, 1) if size is None else size
        self.pitch = 5.0 if pitch is None else pitch
        self.xwidth = 0.5 if xwidth is None else xwidth
        self.ywidth = 0.5 if ywidth is None else ywidth
        self.separation = 0.5 if separation is None else separation

    def create(self, pattern: GridPattern, filename: str) -> CapacitiveGrid:
        grid = CapacitiveGrid(filename,
                              size = self.size,
                              pitch = self.pitch,
                              xwidth = self.xwidth,
                              ywidth = self.ywidth,
                              separation = self.separation)
        if pattern is GridPattern.Interleaved:
            create_interleaved_grid(grid)
        elif pattern is GridPattern.Diamond:
            create_diamond_grid(grid)
        grid.save()
