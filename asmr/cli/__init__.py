""" Commandline Tool """

import click

import asmr.cli.build
import asmr.cli.dev
import asmr.cli.mcu
import asmr.cli.project
import asmr.cli.software
import asmr.cli.test



@click.group(help="ASMR Labs command-line tool.")
@click.version_option()
def main():
    """ cli entrypoint """
    pass


main.add_command(test.main)
main.add_command(build.main)
main.add_command(mcu.main)
main.add_command(dev.main)
main.add_command(project.new)
main.add_command(software.update)


@main.command('testing')
def general_testing():
    """ easy testing command. """
    import asmr.mcu.cmsis
    asmr.mcu.cmsis.fetch_core_headers()
    asmr.mcu.inventory[2].fetch_software()


if __name__ == '__main__':
    main()
