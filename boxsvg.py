'''
Get width, height, depth, and a few other parameters, and accordingly generate an SVG for cutting
a box of that dimensions and specifications.
'''


def _dashedline(p1, p2, dashes = 5):
    '''Generate a dashed line from x1,y1 to x2,y2 with 
    dashes number of dashes.
    '''
    x1, y1 = p1
    x2, y2 = p2
    lines = []  # Collector
    steps = dashes * 2 + 1  # Because it starts and ends with blank!
    xstep, ystep = (x2 - x1) / steps, (y2 - y1) / steps
    for s in range(1, steps, 2):
        lines.append([x1 + s * xstep, y1 + s * ystep, x1 + (s + 1) * xstep, y1 + (s + 1) * ystep])
    return lines


def boxsvg(WIDTH,
           HEIGHT,
           DEPTH,
           OPENABLEFLAP = None,
           CLOSEDFLAP = None,
           DASHES = 5,
           outfilename = None,
           ):
    # WIDTH, HEIGHT, DEPTH - dimensions
    # OPENANBLEFLAP - width of flaps that will open (autocalculated if needed)
    # CLOSEDFLAP - width of fixes flaps (autocalculated if needed)
    # DASHES - number of cut dashes on perforations
    # Outfilename - with path for SVG

    lines = []  # Collector of lines (master, to be forwarded to file later)
    # Autocalculate flaps
    if not OPENABLEFLAP: OPENABLEFLAP = (WIDTH + HEIGHT + DEPTH) / 24
    if not CLOSEDFLAP: CLOSEDFLAP = (WIDTH + HEIGHT + DEPTH) / 18

    # Create front face
    # Set key points first
    PA = 0, 0
    PB = WIDTH, 0
    PC = 0, HEIGHT
    PD = WIDTH, HEIGHT
    lines.extend(_dashedline(PA, PB, DASHES))
    lines.extend(_dashedline(PA, PC, DASHES))
    lines.extend(_dashedline(PC, PD, DASHES))
    lines.extend(_dashedline(PB, PD, DASHES))

    # Right face
    PE = WIDTH + DEPTH, 0
    PF = WIDTH + DEPTH, HEIGHT
    lines.extend(_dashedline(PB, PE, DASHES))
    lines.extend(_dashedline(PD, PF, DASHES))
    lines.extend(_dashedline(PE, PF, DASHES))

    # Left face
    PI = -DEPTH, 0
    PJ = -DEPTH, HEIGHT
    lines.extend(_dashedline(PA, PI, DASHES))
    lines.extend(_dashedline(PC, PJ, DASHES))
    lines.append([PI[0], PI[1], PI[0], PI[1] + CLOSEDFLAP])
    lines.append([PJ[0], PJ[1], PJ[0], PJ[1] - CLOSEDFLAP])

    # Back face
    PG = PE[0] + WIDTH, 0
    PH = PE[0] + WIDTH, HEIGHT
    lines.append([PE[0], PE[1], PG[0], PG[1]])
    lines.append([PF[0] + CLOSEDFLAP, PF[1], PH[0] - CLOSEDFLAP, PH[1]])
    lines.append([PG[0], PG[1] + CLOSEDFLAP, PH[0], PH[1] - CLOSEDFLAP])

    # Top face
    PK = 0, -DEPTH
    PL = WIDTH, -DEPTH
    lines.append([PA[0], PA[1], PK[0], PK[1]])
    lines.append([PB[0], PB[1], PL[0], PL[1]])
    lines.append([PK[0], PK[1], PK[0] + OPENABLEFLAP, PK[1]])
    lines.append([PL[0], PL[1], PL[0] - OPENABLEFLAP, PL[1]])
    PKO = PK[0] + OPENABLEFLAP, PK[1]
    PLO = PL[0] - OPENABLEFLAP, PL[1]
    lines.extend(_dashedline(PKO, PLO, DASHES))

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
    lines.append([PI[0], PI[1] + CLOSEDFLAP * .5, PI[0] - CLOSEDFLAP, PI[1] + CLOSEDFLAP,
                  PJ[0] - CLOSEDFLAP, PJ[1] - CLOSEDFLAP, PJ[0], PJ[1] - 0.5 * CLOSEDFLAP])
    PIO = PI[0], PI[1] + CLOSEDFLAP
    PJO = PJ[0], PJ[1] - CLOSEDFLAP
    lines.extend(_dashedline(PIO, PJO, DASHES))

    # Back face
    lines.append([PG[0], PG[1], PG[0] + CLOSEDFLAP, PG[1], PH[0] + CLOSEDFLAP, PH[1],
                  PH[0], PH[1], PH[0], PH[1] + CLOSEDFLAP, PF[0], PF[1] + CLOSEDFLAP, PF[0], PF[1]])

    # Top face
    lines.append([PK[0], PK[1], PK[0] + OPENABLEFLAP, PK[1] - OPENABLEFLAP,
                  PL[0] - OPENABLEFLAP, PL[1] - OPENABLEFLAP, PL[0], PL[1]])

    # Bottom face
    lines.append([PM[0] + CLOSEDFLAP * 0.5, PM[1], PM[0] + CLOSEDFLAP, PM[1] + CLOSEDFLAP,
                  PN[0] - CLOSEDFLAP, PN[1] + CLOSEDFLAP, PN[0] - 0.5 * CLOSEDFLAP, PN[1]])
    PMO = PM[0] + CLOSEDFLAP, PM[1]
    PNO = PN[0] - CLOSEDFLAP, PN[1]
    lines.extend(_dashedline(PMO, PNO, DASHES))

    # # Export to SVG!

    import svggen
    if not outfilename: outfilename = 'boxsvg.svg'
    svggen.gensvg(lines, outfilename, xoffset = DEPTH + CLOSEDFLAP, yoffset = DEPTH + OPENABLEFLAP)

###########
# Self test


if __name__ == '__main__':
    boxsvg(100, 100, 50, 20, 20)
