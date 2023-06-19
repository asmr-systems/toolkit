import copy
from enum import Enum

import svgwrite
from svgwrite import mm

import asmr.kicad
from .gfx import Line, Rectangle, Diamond, SVG


class GridPattern(Enum):
    Interleaved = 'interleaved'
    Diamond     = 'diamond'


class CapacitiveGrid:
    def __init__(self,
                 filename: str,
                 size=(1, 1),          # (X, Y)
                 pitch=5,              # width|height of button (mm)
                 xwidth=0.5,           # width of x electrode traces
                 ywidth=0.5,           # width of y electrode traces
                 separation=0.5,       # min separation between electrodes
                 margin=0,             # margin around entire sensor perimeter
                 padding=0,            # padding within each sensor node
                 use_color=False,      # display different color electrodes
                 n_columns_per_pad=1 , # each column pad is 2 columns
                 n_rows_per_pad=1,     # each row pad is 2 rows
                 silk_scaling=(1, 1),
                 mask_electrodes=(False, True), # cover electrodes in solder mask
                 fmt='1.0|1.0'):       # format string
        isExtensionless = len(filename.split('.')) < 2 # TODO check valid extensions
        self.ext = 'svg' if isExtensionless else filename.split('.')[-1]
        self.filename = f'{filename}.{fmt}' if isExtensionless else filename
        self.size = size
        self.pitch = pitch
        self.xwidth = xwidth
        self.ywidth = ywidth
        self.separation = separation
        self.margin = margin
        self.padding = padding
        self.use_color = use_color
        self.n_columns_per_pad = n_columns_per_pad
        self.n_rows_per_pad = n_rows_per_pad
        self.silk_grid_scale_x = silk_scaling[0]
        self.silk_grid_scale_y = silk_scaling[1]
        self.mask_electrode_x = mask_electrodes[0]
        self.mask_electrode_y = mask_electrodes[1]
        self.fmt_str = fmt
        self.fmt = (
            {'fill': 6.0, 'pattern': '#'},
            {'fill': 6.0, 'pattern': '#'}
        )
        self.layers = {
            'electrodes': [],
            'solder_mask': [],
            'silkscreen': [],
        }

        self.colors = {
            'x': '#ed53ba',
            'y': '#2b78fc',
            'silkscreen' : '#b62ed1B0',
            'solder_mask': '#86ff3b57',
        }
        self.parse_fmt()

    def parse_fmt(self):
        row_col = self.fmt_str.split('|')
        for i in range(len(row_col)):
            float_pattern = row_col[i].split(',')
            self.fmt[i]['fill'] = float(float_pattern[0])
            if len(float_pattern) == 2:
                self.fmt[i]['pattern'] = float_pattern[1]

    def save(self):
        if (self.ext == 'svg'):
            self.save_svg()
        elif self.ext == "kicad_mod":
            self.save_kicad_footprint()

    def save_svg(self):
        svg = SVG(
            self.filename,
            [
                *self.layers['electrodes'],
                *self.layers['solder_mask'],
                *self.layers['silkscreen'],
            ])
        svg.save()

    def save_kicad_footprint(self):
        footprint = asmr.kicad.Footprint(self.filename)
        footprint.pads_from_shapes(self.layers['electrodes'])
        footprint.mask_from_shapes(self.layers['solder_mask'])
        footprint.silkscreen_from_shapes(self.layers['silkscreen'])
        footprint.save()


# TODO: incorporate grid x and y scale
def create_inverted_square_grid(grid: CapacitiveGrid, layer='solder_mask'):
    size = grid.pitch - grid.xwidth

    if grid.margin > 0:
        for column in range(grid.size[0]+2):
            x0 = (column-1)*grid.pitch + grid.margin + grid.xwidth
            if column == 0:
                x0 = 0
            y0 = 0
            x1 = x0 + size
            if column == 0 or column == grid.size[0]+1:
                x1 = x0 + grid.margin
            y1 = grid.margin
            grid.layers[layer].append(Rectangle(
                x0,
                y0,
                x1,
                y1,
                width=grid.xwidth,
                fill=True,
                color=grid.colors[layer] if grid.use_color else '#000000',
                group=layer,
            ))
            grid.layers[layer].append(Rectangle(
                x0,
                y0 + grid.margin + grid.size[1]*grid.pitch + grid.xwidth,
                x1,
                y1 + grid.margin + grid.size[1]*grid.pitch + grid.xwidth,
                width=grid.xwidth,
                fill=True,
                color=grid.colors[layer] if grid.use_color else '#000000',
                group=layer,
            ))

        for row in range(grid.size[1]):
            x0 = 0
            y0 = row*grid.pitch + grid.margin + grid.xwidth
            x1 = x0 + grid.margin
            y1 = y0 + size
            grid.layers[layer].append(Rectangle(
                x0,
                y0,
                x1,
                y1,
                width=grid.xwidth,
                fill=True,
                color=grid.colors[layer] if grid.use_color else '#000000',
                group=layer,
            ))
            grid.layers[layer].append(Rectangle(
                x0 + grid.margin + grid.size[0]*grid.pitch + grid.xwidth,
                y0,
                x1 + grid.margin + grid.size[0]*grid.pitch + grid.xwidth,
                y1,
                width=grid.xwidth,
                fill=True,
                color=grid.colors[layer] if grid.use_color else '#000000',
                group=layer,
            ))

    for column in range(grid.size[0]):
        for row in range(grid.size[1]):
            x0 = column*grid.pitch + grid.margin + grid.xwidth
            y0 = row*grid.pitch + grid.margin + grid.xwidth
            grid.layers[layer].append(Rectangle(
                x0,
                y0,
                x0+size,
                y0+size,
                width=grid.xwidth,
                fill=True,
                color=grid.colors[layer] if grid.use_color else '#000000',
                group=layer,
            ))

def create_square_grid(grid: CapacitiveGrid, layer='silkscreen'):
    x_scale = grid.silk_grid_scale_x
    y_scale = grid.silk_grid_scale_y
    x_offset = grid.ywidth/2
    y_offset = grid.xwidth/2

    for column in range(int(grid.size[0]/y_scale) + 1):
        xcenter = column*grid.pitch*y_scale + x_offset
        ylength = grid.pitch * grid.size[1] + grid.ywidth
        grid.layers[layer].append(Line(
            xcenter + grid.margin,
            0,
            xcenter + grid.margin,
            ylength + grid.margin*2,
            width=grid.xwidth,
            color=grid.colors[layer] if grid.use_color else '#000000',
            group=layer,
        ))

    for row in range(int(grid.size[1]/x_scale) + 1):
        y_start = row*grid.pitch*x_scale + y_offset
        xlength = grid.pitch*grid.size[0] + grid.xwidth
        grid.layers[layer].append(Line(
            0,
            y_start + grid.margin,
            xlength + grid.margin*2,
            y_start + grid.margin,
            width=grid.ywidth,
            color=grid.colors[layer] if grid.use_color else '#000000',
            group=layer,
        ))

def create_interleaved_grid(grid: CapacitiveGrid, layer='electrodes'):
    # calculate space between x-y electrodes from target separation
    ydigits_per_node = 0
    remaining_space = grid.pitch - grid.xwidth - 2*grid.padding
    while remaining_space > (2*ydigits_per_node*grid.separation):
        ydigits_per_node += 1
        remaining_space = (grid.pitch - 2*grid.padding) - ydigits_per_node*((grid.xwidth + grid.ywidth)/2)
    ydigits_per_node -= 1
    remaining_space = (grid.pitch - 2*grid.padding) - ydigits_per_node*(grid.xwidth + grid.ywidth)
    grid.separation = remaining_space / (2*ydigits_per_node)
    # n_xdigits = (ydigits_per_node * grid.size[1]) + 1
    xdigits_per_node = ydigits_per_node + 1
    dy_xdigits = grid.separation*2 + grid.ywidth + grid.xwidth

    x_offset = grid.ywidth/2
    y_offset = grid.xwidth/2

    for column in range(grid.size[0]):
        group = f'pad={int(grid.size[1]/grid.n_rows_per_pad) + int((column-(column%grid.n_columns_per_pad))/grid.n_columns_per_pad)+1}'

        # create X columns
        xcenter = column*grid.pitch + grid.pitch/2 + x_offset
        ylength = grid.pitch * grid.size[1]
        grid.layers[layer].append(Line(
            xcenter + grid.margin,
            y_offset + grid.margin,
            xcenter + grid.margin,
            ylength + y_offset + grid.margin,
            width=grid.xwidth,
            color=grid.colors['x'] if grid.use_color else '#000000',
            group=group,
        ))

        # iterate over columnar buttons
        for node in range(grid.size[1]):
            # the minimum columnar digits (surrounding each node)
            min_x_digits = grid.size[1] + 1
            node_y_offset = node * grid.pitch + grid.padding
            x_length = (grid.pitch - 2*grid.padding) - grid.ywidth - (2*grid.separation) - grid.xwidth
            for digit in range(xdigits_per_node):
                x_start = xcenter - (x_length/2)
                x_end   = xcenter + (x_length/2)
                y = node_y_offset + digit * dy_xdigits + y_offset
                grid.layers[layer].append(Line(
                    x_start + grid.margin,
                    y + grid.margin,
                    x_end + grid.margin,
                    y + grid.margin,
                    width=grid.xwidth,
                    color=grid.colors['x'] if grid.use_color else '#000000',
                    linecap='round',
                    group=group,
                ))

    # create row electrode patterns
    for row in range(grid.size[1]):
        group = f'pad={int((row-(row%grid.n_rows_per_pad))/grid.n_rows_per_pad) + 1}'

        y_start = row*grid.pitch + grid.xwidth + grid.separation + y_offset + grid.padding
        ylength = grid.pitch - grid.xwidth - grid.ywidth - grid.separation*2 - 2*grid.padding
        for column in range(grid.size[0]):
            xcenter = column*grid.pitch + x_offset + grid.padding

            # column line
            grid.layers[layer].append(Line(
                xcenter + grid.margin,
                y_start + grid.margin,
                xcenter + grid.margin,
                y_start+ylength + grid.margin,
                width=grid.ywidth,
                color=grid.colors['y'] if grid.use_color else '#000000',
                group=group,
            ))
            button_width = grid.pitch - 2*grid.padding
            grid.layers[layer].append(Line(
                xcenter + grid.margin + button_width,
                y_start + grid.margin,
                xcenter + grid.margin + button_width,
                y_start+ylength + grid.margin,
                width=grid.ywidth,
                color=grid.colors['y'] if grid.use_color else '#000000',
                group=group,
            ))


            # fingers
            for digit in range(ydigits_per_node):
                digit_y = y_start + digit*(grid.xwidth + 2*grid.separation + grid.ywidth)
                digit_length = None
                digit_x_start = None
                for side in range(2):
                    if side == 0:
                        # when side = 0, its the left side of the electrode
                        digit_x_start = xcenter
                        digit_length  = (grid.pitch + 2*grid.padding)/2 - grid.xwidth/2 - grid.separation - grid.ywidth/2 - 2*grid.padding
                    elif side == 1:
                        # when side = 1, its the right hand side of the electrode
                        digit_x_start = xcenter + button_width
                        digit_length  = -((grid.pitch + 2*grid.padding)/2 - grid.xwidth/2 - grid.separation - grid.ywidth/2 - 2*grid.padding)

                    grid.layers[layer].append(Line(
                        digit_x_start + grid.margin,
                        digit_y + grid.margin,
                        digit_x_start + digit_length + grid.margin,
                        digit_y + grid.margin,
                        width=grid.ywidth,
                        color=grid.colors['y'] if grid.use_color else '#000000', #'#00FF00' if side == 0 else '#FFFF00',
                        linecap='round',
                        group=group,
                    ))

            # this button column is not on the end: draw a line connecting to the next electrode in the row
            if column < (grid.size[0] - 1):
                grid.layers[layer].append(Line(
                    xcenter + grid.margin + button_width,
                    y_start + grid.margin + ylength/2,
                    (column+1)*grid.pitch + x_offset + grid.padding,
                    y_start + grid.margin + ylength/2,
                    width=grid.ywidth,
                    color=grid.colors['y'] if grid.use_color else '#000000', #'#00FF00' if side == 0 else '#FFFF00',
                    linecap='round',
                    group=group,
                ))



def create_diamond_grid(grid: CapacitiveGrid, layer='electrodes'):
    # Y electrodes
    for column in range(grid.size[0] + 1):
        for row in range(grid.size[1]):
            #group = f'pad={row + 1}'
            group = f'pad={int((row-(row%grid.n_rows_per_pad))/grid.n_rows_per_pad) + 1}'
            cutoff = 'none'
            if column == 0:
                cutoff = 'left'
            elif column == grid.size[0]:
                cutoff = 'right'
            xpadding = grid.margin
            ypadding = grid.margin + grid.separation + grid.xwidth/2
            diamond = Diamond(
                grid.pitch*column + xpadding,
                grid.pitch*row + ypadding,
                grid.pitch - 2*grid.separation,
                color=grid.colors['x'] if grid.use_color else '#000000',
                fill = grid.fmt[0]['fill'],
                stroke_width = grid.xwidth,
                group=group,
                pattern=grid.fmt[0]['pattern'],
                cutoff = cutoff,
            )
            grid.layers[layer].append(diamond)
            if column < grid.size[0]:
                # add horizontal connector line
                grid.layers[layer].append(Line(
                    diamond.x1,
                    diamond.y1,
                    diamond.x1 + grid.separation*2 + grid.xwidth,
                    diamond.y1,
                    width=min(grid.separation/2, grid.xwidth),
                    color=grid.colors['x'] if grid.use_color else '#000000',
                    linecap='round',
                    group=group,
                ))
    # X electrodes
    for column in range(grid.size[0]):
        for row in range(grid.size[1] + 1):
            #group = f'pad={grid.size[1] + column + 1}'
            group = f'pad={int(grid.size[1]/grid.n_rows_per_pad) + int((column-(column%grid.n_columns_per_pad))/grid.n_columns_per_pad)+1}'

            cutoff = 'none'
            if row == 0:
                cutoff = 'top'
            elif row == grid.size[1]:
                cutoff = 'bottom'
            xpadding = grid.margin
            ypadding = grid.margin + grid.separation + grid.xwidth/2
            grid.layers[layer].append(Diamond(
                grid.pitch*column + grid.pitch/2 + xpadding,
                grid.pitch*row - grid.pitch/2 + ypadding,
                grid.pitch - 2*grid.separation,
                color=grid.colors['y'] if grid.use_color else '#000000',
                fill = grid.fmt[1]['fill'],
                stroke_width = grid.xwidth,
                group=group,
                pattern=grid.fmt[1]['pattern'],
                cutoff = cutoff,
            ))

def generate_solder_mask(grid: CapacitiveGrid):
    if not grid.mask_electrode_x and not grid.mask_electrode_y:
        create_inverted_square_grid(grid)
        return

    if grid.mask_electrode_y and not grid.mask_electrode_x:
        for electrode in grid.layers['electrodes']:
            n = int(electrode.group.split('=')[1])
            if n > grid.size[0]:
                e = copy.deepcopy(electrode)
                e.group = 'solder_mask'
                e.color= grid.colors['solder_mask']
                grid.layers['solder_mask'].append(e)
    if grid.mask_electrode_x and not grid.mask_electrode_y:
        for electrode in grid.layers['electrodes']:
            n = int(electrode.group.split('=')[1])
            if n <= grid.size[0]:
                e = copy.deepcopy(electrode)
                e.group = 'solder_mask'
                e.color= grid.colors['solder_mask']
                grid.layers['solder_mask'].append(e)



class CapacitiveGridGenerator:
    def __init__(self,
                 size=(1, 1),
                 pitch=5,
                 xwidth=0.5,
                 ywidth=0.5,
                 separation=0.5,
                 padding=0,
                 resolution=(1, 1),
                 silk_scaling=(1, 1),
                 use_color=False,
                 fmt='1.0|1.0'):
        self.size = (1, 1) if size is None else size
        self.pitch = 5.0 if pitch is None else pitch
        self.xwidth = 0.5 if xwidth is None else xwidth
        self.ywidth = 0.5 if ywidth is None else ywidth
        self.separation = 0.5 if separation is None else separation
        self.padding = 0 if padding is None else padding
        self.resolution = (1, 1) if resolution is None else resolution
        self.silk_scaling = (1, 1) if silk_scaling is None else silk_scaling
        self.use_color = False if use_color is None else use_color
        self.fmt = '1.0|1.0' if fmt is None else fmt

    def create(self, pattern: GridPattern, filename: str) -> CapacitiveGrid:
        grid = CapacitiveGrid(filename,
                              size = self.size,
                              pitch = self.pitch,
                              xwidth = self.xwidth,
                              ywidth = self.ywidth,
                              separation = self.separation,
                              padding = self.padding,
                              n_columns_per_pad=self.resolution[0],
                              n_rows_per_pad=self.resolution[1],
                              silk_scaling=self.silk_scaling,
                              use_color = self.use_color,
                              fmt=self.fmt)
        if pattern is GridPattern.Interleaved:
            create_interleaved_grid(grid)
            create_square_grid(grid)
            generate_solder_mask(grid)
        elif pattern is GridPattern.Diamond:
            create_diamond_grid(grid)
            create_square_grid(grid)
            generate_solder_mask(grid)

        grid.save()
