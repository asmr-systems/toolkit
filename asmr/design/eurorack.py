import svgwrite
from svgwrite import mm

from .gfx import Rectangle, SVG

# panel hp/u are adjusted to take the case spacing into account.
#
# see for more details:
# * https://www.doepfer.de/a100_man/a100m_e.htm
# * https://intellijel.com/support/1u-technical-specifications/
MM_PER_HU           = 44.45
MM_HU_MARGIN        = 4.85
MM_HU_PCB_MARGIN    = 23.35/2
MM_HP_PCB_MARGIN    = 2.0/2
PANEL_MM_PER_HP     = 5.0
MOUNT_HOLE_DIA      = 3.2
MOUNT_HOLE_X_OFFSET = 7.5
MOUNT_HOLE_Y_OFFSET = 3.0

class EurorackPanel:
    def __init__(self, filename, hp, hu, ovals=True, pcb_zone=False):
        self.filename       = filename
        self.outline        = []
        self.ovals          = ovals
        self.show_pcb_zone  = pcb_zone
        self.width          = hp * PANEL_MM_PER_HP
        self.height         = (hu * MM_PER_HU) - MM_HU_MARGIN
        self.max_pcb_height = (hu * MM_PER_HU) - MM_HU_PCB_MARGIN
        self.max_pcb_width  = (hp * PANEL_MM_PER_HP) - MM_HP_PCB_MARGIN
        self.linewidth      = 0.05

    def render(self):
        # panel outline
        self.outline.append(Rectangle(
            0, # x0
            0, # y0
            self.width,
            self.height,
            width=self.linewidth,
            fill=False,
        ))

        if self.show_pcb_zone:
            self.outline.append(Rectangle(
                MM_HP_PCB_MARGIN, # x0
                MM_HU_PCB_MARGIN, # y0
                self.width - MM_HP_PCB_MARGIN,
                self.height - MM_HU_PCB_MARGIN,
                width=self.linewidth,
                fill=False,
                color="#FF0000",
            ))


        # mounting holes
        xs = []
        ys = []
        width = MOUNT_HOLE_DIA
        if self.ovals:
            xs = [MOUNT_HOLE_X_OFFSET-(MOUNT_HOLE_DIA),
              self.width - (MOUNT_HOLE_X_OFFSET+(MOUNT_HOLE_DIA)),
              self.width -(MOUNT_HOLE_X_OFFSET+(MOUNT_HOLE_DIA)),
              MOUNT_HOLE_X_OFFSET-(MOUNT_HOLE_DIA),
              ]
            ys = [MOUNT_HOLE_Y_OFFSET-(MOUNT_HOLE_DIA/2),
              MOUNT_HOLE_Y_OFFSET-(MOUNT_HOLE_DIA/2),
              self.height - MOUNT_HOLE_Y_OFFSET-(MOUNT_HOLE_DIA/2),
              self.height - MOUNT_HOLE_Y_OFFSET-(MOUNT_HOLE_DIA/2),
              ]
            width = MOUNT_HOLE_DIA * 2
        else:
            xs = [MOUNT_HOLE_X_OFFSET-(MOUNT_HOLE_DIA/2),
              self.width - (MOUNT_HOLE_X_OFFSET+(MOUNT_HOLE_DIA/2)),
              self.width -(MOUNT_HOLE_X_OFFSET+(MOUNT_HOLE_DIA/2)),
              MOUNT_HOLE_X_OFFSET-(MOUNT_HOLE_DIA/2),
              ]
            ys = [MOUNT_HOLE_Y_OFFSET-(MOUNT_HOLE_DIA/2),
              MOUNT_HOLE_Y_OFFSET-(MOUNT_HOLE_DIA/2),
              self.height - MOUNT_HOLE_Y_OFFSET-(MOUNT_HOLE_DIA/2),
              self.height - MOUNT_HOLE_Y_OFFSET-(MOUNT_HOLE_DIA/2),
              ]
            width = MOUNT_HOLE_DIA
        self.render_mounting_holes(xs, ys, width)

    def render_mounting_holes(self, xs, ys, width):
        for i in range(len(xs)):
            self.outline.append(Rectangle(
                xs[i],
                ys[i],
                xs[i] + width,
                ys[i] + MOUNT_HOLE_DIA,
                rx=MOUNT_HOLE_DIA/2,
                ry=MOUNT_HOLE_DIA/2,
                width=self.linewidth,
                fill=False,
            ))

    def save(self):
        svg = SVG(
            self.filename,
            self.outline
        )
        svg.save()
