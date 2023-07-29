""" ASMR Design Toolkit """

import click

import asmr.logging
import asmr.design
import asmr.kicad


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()


@click.group('design', help="generate various cad designs")
def main():
    pass


@main.command("touch-grid")
@click.option('-p', '--pattern',
              default='interleaved',
              type=click.Choice(['interleaved', 'diamond'], case_sensitive=False),
              help="output file (.svg)")
@click.option('-x', '--xsize', default=1, help="X size", type=int)
@click.option('-y', '--ysize', default=1, help="Y size", type=int)
@click.option('--pitch', default=6.0, help="node size (mm)", type=float)
@click.option('--xwidth', default=0.5, help="width of x electrode traces (mm)", type=float)
@click.option('--ywidth', default=0.5, help="width of y electrode traces (mm)", type=float)
@click.option('-s', '--separation', default=0.3, help="separation of traces", type=float)
@click.option('--padding', default=0.0, help="padding of sensor nodes", type=float)
@click.option('-r', '--resolution', default=(1, 1), help="scale of rows/columns", type=(int, int))
@click.option('--silk_scaling', default=(1, 1), help="scale of silkscreen rows/columns", type=(int, int))
@click.option('-f', '--filename', required=True, help="output file (.svg|.kicad_mod)")
@click.option('--fmt', default='0.6,#|0.6,#', help="row|column format string (<FILL_PERCENT>[,<PATTERN>][|][...]) PATTERN=/ \ #")
@click.option('--color', is_flag=True, default=False, help="color-codes electrodes for easier inspection")
def touch_grid(filename,
               pattern,
               xsize,
               ysize,
               pitch,
               xwidth,
               ywidth,
               separation,
               padding,
               resolution,
               silk_scaling,
               fmt,
               color):
    """ generate capacitive touch design. """
    if pattern == 'interleaved':
        pattern = asmr.design.GridPattern.Interleaved
    elif pattern == 'diamond':
        pattern = asmr.design.GridPattern.Diamond

    grid = asmr.design.CapacitiveGridGenerator(size=(xsize, ysize),
                                               pitch=pitch,
                                               xwidth=xwidth,
                                               ywidth=ywidth,
                                               separation=separation,
                                               padding=padding,
                                               resolution=resolution,
                                               silk_scaling=silk_scaling,
                                               use_color=color,
                                               fmt=fmt)

    grid.create(pattern, filename)

@main.command("kicad-symbol")
@click.option('-p', '--pins', default=1, help="number of pins", type=int)
@click.option('-f', '--filename', required=True, help="output file (.svg|.kicad_mod)")
def kicad_symbol(pins, filename):
    """ generate a kicad symbol. """
    sym = asmr.kicad.Symbol(filename, pins)
    sym.save()
