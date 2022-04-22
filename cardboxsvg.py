'''
Get width, height, depth, and a few other parameters, and accordingly generate an SVG for cutting
a box of that dimensions and specifications.
'''


def _dashedline(p1, p2, dashes=5, density=0):
    '''Generate a dashed line from x1,y1 to x2,y2 with
    dashes number of dashes and given density. Density=0 means 50% is perforated, but value ranging
    -.49 to +.49 changes it from nearly invisible to fully perforated.
    '''
    if density <= -.5: density = -.499
    if density >= .5: density = .499
    x1, y1 = p1
    x2, y2 = p2
    lines = []  # Collector
    steps = dashes * 2 + 1  # Because it starts and ends with blank!
    xstep, ystep = (x2 - x1) / steps, (y2 - y1) / steps
    for s in range(1, steps, 2):
        #lines.append([x1 + s * xstep, y1 + s * ystep, x1 + (s + 1) * xstep, y1 + (s + 1) * ystep])
        lines.append([x1 + (s - density) * xstep, y1 + (s - density) * ystep,
                      x1 + (s + 1 + density) * xstep, y1 + (s + 1 + density) * ystep])
    return lines


def boxsvg(WIDTH,
           HEIGHT,
           DEPTH,
           OPENABLEFLAP=None,
           CLOSEDFLAP=None,
           DASHES=5,
           DASHDENSITY=0,
           OUTFILENAME=None,
           SLOTWIDTH=1,
           ):
    # WIDTH, HEIGHT, DEPTH - dimensions
    # OPENANBLEFLAP - width of flaps that will open (autocalculated if needed)
    # CLOSEDFLAP - width of fixed flaps (autocalculated if needed)
    # DASHES - number of cut dashes on perforations
    # DASHDENSITY - percentage (-50..+50) offset of dashed lines' density
    # OUTFILENAME - with path for SVG
    # SLOTWIDTH - how wide will the slot be for the static flaps

    lines = []  # Collector of lines (master, to be forwarded to file later)
    # Autocalculate flaps
    if not OPENABLEFLAP: OPENABLEFLAP = WIDTH / 5
    if not CLOSEDFLAP: CLOSEDFLAP = WIDTH / 5

    # Create front face
    # Set key points first
    PA = 0, 0
    PB = WIDTH, 0
    PC = 0, HEIGHT
    PD = WIDTH, HEIGHT
    lines.extend(_dashedline(PA, PB, DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PA, PC, DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PC, PD, DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PB, PD, DASHES, DASHDENSITY / 100))

    # Right face
    PE = WIDTH + DEPTH, 0
    PF = WIDTH + DEPTH, HEIGHT
    lines.extend(_dashedline(PB, PE, DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PD, PF, DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PE, PF, DASHES, DASHDENSITY / 100))

    # Left face
    PI = -DEPTH, 0
    PJ = -DEPTH, HEIGHT
    lines.extend(_dashedline(PA, PI, DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PC, PJ, DASHES, DASHDENSITY / 100))
    lines.append([PI[0], PI[1], PI[0], PI[1] + CLOSEDFLAP])
    lines.append([PJ[0], PJ[1], PJ[0], PJ[1] - CLOSEDFLAP])

    # Back face
    PG = PE[0] + WIDTH, 0
    PH = PE[0] + WIDTH, HEIGHT
    lines.extend(_dashedline(PF, [PF[0] + CLOSEDFLAP, PF[1]], DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PH, [PH[0] - CLOSEDFLAP, PH[1]], DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PG, [PG[0], PG[1] + CLOSEDFLAP], DASHES, DASHDENSITY / 100))
    lines.extend(_dashedline(PH, [PH[0], PH[1] - CLOSEDFLAP], DASHES, DASHDENSITY / 100))
    lines.append([PE[0], PE[1], PG[0], PG[1]])
    lines.append([PF[0] + CLOSEDFLAP, PF[1], PH[0] - CLOSEDFLAP, PH[1],
                  PH[0] - CLOSEDFLAP, PH[1] + SLOTWIDTH,
                  PF[0] + CLOSEDFLAP, PH[1] + SLOTWIDTH,
                  PF[0] + CLOSEDFLAP, PF[1]])
    lines.append([PG[0], PG[1] + CLOSEDFLAP, PH[0], PH[1] - CLOSEDFLAP,
                  PH[0] + SLOTWIDTH, PH[1] - CLOSEDFLAP,
                  PH[0] + SLOTWIDTH, PG[1] + CLOSEDFLAP,
                  PG[0], PG[1] + CLOSEDFLAP])

    # Top face
    PK = 0, -DEPTH
    PL = WIDTH, -DEPTH
    PKO = PK[0] + OPENABLEFLAP, PK[1]
    PLO = PL[0] - OPENABLEFLAP, PL[1]
    lines.extend(_dashedline(PKO, PLO, DASHES, DASHDENSITY / 100))
    lines.append([PA[0], PA[1], PK[0], PK[1]])
    lines.append([PB[0], PB[1], PL[0], PL[1]])
    lines.append([PK[0], PK[1], PK[0] + OPENABLEFLAP, PK[1]])
    lines.append([PL[0], PL[1], PL[0] - OPENABLEFLAP, PL[1]])

    # Bottom face
    PM = PC[0], PC[1] + DEPTH
    PN = PD[0], PD[1] + DEPTH
    lines.append([PC[0], PC[1], PM[0], PM[1]])
    lines.append([PD[0], PD[1], PN[0], PN[1]])
    lines.append([PM[0], PM[1], PM[0] + CLOSEDFLAP, PM[1]])
    lines.append([PN[0], PN[1], PN[0] - CLOSEDFLAP, PN[1]])

    # # FLAPS

    # Right face
    lines.append([PB[0], PB[1], PB[0] + OPENABLEFLAP, PB[1] - OPENABLEFLAP,
                  PE[0], PE[1] - OPENABLEFLAP, PE[0], PE[1]])
    lines.append([PD[0], PD[1], PD[0] + CLOSEDFLAP, PD[1] + CLOSEDFLAP,
                  PF[0] - CLOSEDFLAP, PF[1] + CLOSEDFLAP, PF[0], PF[1]])

    # Left face
    lines.append([PA[0], PA[1], PA[0] - OPENABLEFLAP, PA[1] - OPENABLEFLAP,
                  PI[0], PI[1] - OPENABLEFLAP, PI[0], PI[1]])
    lines.append([PC[0], PC[1], PC[0] - CLOSEDFLAP, PC[1] + CLOSEDFLAP,
                  PJ[0] + CLOSEDFLAP, PJ[1] + CLOSEDFLAP, PJ[0], PJ[1]])
    lines.append([PI[0], PI[1] + CLOSEDFLAP * .8, PI[0] - CLOSEDFLAP, PI[1] + CLOSEDFLAP,
                  PJ[0] - CLOSEDFLAP, PJ[1] - CLOSEDFLAP, PJ[0], PJ[1] - 0.8 * CLOSEDFLAP])
    PIO = PI[0], PI[1] + CLOSEDFLAP
    PJO = PJ[0], PJ[1] - CLOSEDFLAP
    lines.extend(_dashedline(PIO, PJO, DASHES, DASHDENSITY / 100))

    # Back face
    lines.append([PG[0], PG[1], PG[0] + CLOSEDFLAP, PG[1] + CLOSEDFLAP * .3, PH[0] + CLOSEDFLAP, PH[1] - CLOSEDFLAP * .3,
                  PH[0], PH[1], PH[0] - CLOSEDFLAP * .3, PH[1] +
                  CLOSEDFLAP, PF[0] + CLOSEDFLAP * .3, PF[1] + CLOSEDFLAP,
                  PF[0], PF[1]])

    # Top face
    lines.append([PK[0] + OPENABLEFLAP, PK[1], PK[0] + OPENABLEFLAP, PK[1] - OPENABLEFLAP * .2,
                  PK[0], PK[1] - OPENABLEFLAP * .2, PK[0] + OPENABLEFLAP, PK[1] - OPENABLEFLAP,
                  PL[0] - OPENABLEFLAP, PL[1] - OPENABLEFLAP, PL[0], PL[1] - OPENABLEFLAP * .2,
                  PL[0] - OPENABLEFLAP, PL[1] - OPENABLEFLAP * .2, PL[0] - OPENABLEFLAP, PL[1]])

    # Bottom face
    lines.append([PM[0] + CLOSEDFLAP * 0.8, PM[1], PM[0] + CLOSEDFLAP, PM[1] + CLOSEDFLAP,
                  PN[0] - CLOSEDFLAP, PN[1] + CLOSEDFLAP, PN[0] - 0.8 * CLOSEDFLAP, PN[1]])
    PMO = PM[0] + CLOSEDFLAP, PM[1]
    PNO = PN[0] - CLOSEDFLAP, PN[1]
    lines.extend(_dashedline(PMO, PNO, DASHES, DASHDENSITY / 100))

    # # Export to SVG!

    import svggen
    if not OUTFILENAME: OUTFILENAME = 'boxsvg.svg'
    svggen.svggen(lines, OUTFILENAME, xoffset=DEPTH + CLOSEDFLAP, yoffset=DEPTH + OPENABLEFLAP)

###########
# Self test


if __name__ == '__main__':
    boxsvg(19, 52, 16, DASHES=5, DASHDENSITY=-15, )
