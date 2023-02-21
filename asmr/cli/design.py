""" ASMR Design Toolkit """

import click

import asmr.logging
import asmr.design


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
@click.option('-s', '--separation', default=0.5, help="separation of traces", type=float)
@click.option('-f', '--filename', required=True, help="output file (.svg)")
def touch_grid(filename, pattern, xsize, ysize, pitch, xwidth, ywidth, separation):
    """ generate capacitive touch design. """
    if pattern == 'interleaved':
        pattern = asmr.design.GridPattern.Interleaved
    elif pattern == 'diamond':
        pattern = asmr.design.GridPattern.Diamond

    grid = asmr.design.CapacitiveGridGenerator(size=(xsize, ysize),
                                               pitch=pitch,
                                               xwidth=xwidth,
                                               ywidth=ywidth,
                                               separation=separation)

    grid.create(pattern, filename)
