'''
Similar to cardbox, but instead of papery or generally thin materials, this one assumes panel
materials with appreciable thicknesses are used, some wood glue, and no flaps or bendable
segments.
'''

import svggen
import math


def boxsvg(
    length,  # In final SVG units. Note these are the box INTERIOR'S dimensions
    width,
    height,
    outfile=None,  # If given, a SVG file to generate. Otherwise just return coordinates list
    thickness=3,  # Panel thickness in the same SVG units
    sideteeth=3,  # Number of catching protrusions at the connected side edges
    bottomteeth=3,  # Number of teeth of the bottom panel (connecting to 4 sides)
    top=True,  # Include the top (lid) side?
    topteeth=2,  # Teeth for the top lid if used (can be 0 for non-meshing simple lid)
):
    # Firstly prepare the master line collector
    masterlines = []

    # GENERATE PANEL GEOMETRY
    # Side panel, lengthwise
    panel = []
    panel.extend(getteeth((thickness, thickness), (length + thickness, thickness), topteeth, -thickness, even=True))
    panel.extend(getteeth((length + thickness, thickness), (length +
                 thickness, thickness + height), sideteeth, -thickness))
    panel.extend(getteeth((length + thickness, thickness + height),
                 (thickness, thickness + height), bottomteeth, -thickness, even=True))
    panel.extend(getteeth((thickness, thickness + height), (thickness, thickness), sideteeth, -thickness, even=True))
    # Add the first one
    masterlines.append(panel)
    # Add the second one
    panel = [(x + length + 3 * thickness, y) for x, y in panel]
    masterlines.append(panel)

    # Side panel, widthwise
    panel = []
    panel.extend(getteeth((thickness, thickness), (width + thickness, thickness), topteeth, -thickness, even=True))
    panel.extend(getteeth((width + thickness, thickness), (width + thickness, thickness + height), sideteeth, -thickness))
    panel.extend(getteeth((width + thickness, thickness + height),
                 (thickness, thickness + height), bottomteeth, -thickness, even=True))
    panel.extend(getteeth((thickness, thickness + height), (thickness, thickness), sideteeth, -thickness, even=True))
    # Displace
    panel = [(x, y + height + 3 * thickness) for x, y in panel]
    # Add the first one
    masterlines.append(panel)
    # And the second one
    panel = [(x + width + thickness * 3, y) for x, y in panel]
    masterlines.append(panel)

    # Bottom panel
    panel = [(0, 0)]  # Top left
    panel.extend(getteeth((thickness, 0), (thickness + length, 0), bottomteeth, thickness, even=True))
    panel.append((length + 2 * thickness, 0))
    panel.extend(getteeth((length + 2 * thickness, thickness), (length + 2 * thickness, thickness + width),
                          bottomteeth, thickness, even=True))
    panel.append((length + 2 * thickness, width + 2 * thickness))
    panel.extend(getteeth((length + thickness, width + 2 * thickness), (thickness, width + 2 * thickness),
                          bottomteeth, thickness, even=True))
    panel.append((0, width + 2 * thickness))
    panel.extend(getteeth((0, width + thickness), (0, thickness), bottomteeth, thickness, even=True))
    panel.append((0, 0))
    # Displace it
    panel = [(x, y + height * 2 + thickness * 6) for x, y in panel]
    masterlines.append(panel)

    # Top lid
    if top:
        panel = [(0, 0)]  # Top left
        panel.extend(getteeth((thickness, 0), (thickness + length, 0), topteeth, thickness, even=True))
        panel.append((length + 2 * thickness, 0))
        panel.extend(getteeth((length + 2 * thickness, thickness), (length + 2 * thickness, thickness + width),
                              topteeth, thickness, even=True))
        panel.append((length + 2 * thickness, width + 2 * thickness))
        panel.extend(getteeth((length + thickness, width + 2 * thickness), (thickness, width + 2 * thickness),
                              topteeth, thickness, even=True))
        panel.append((0, width + 2 * thickness))
        panel.extend(getteeth((0, width + thickness), (0, thickness), topteeth, thickness, even=True))
        panel.append((0, 0))
        # Displace it
        panel = [(x + length + 3 * thickness, y + height * 2 + thickness * 6) for x, y in panel]
        masterlines.append(panel)

    # Generated all geometry. Export
    if outfile: svggen.svggen(masterlines, outfile)
    return masterlines


### TOOTHED LINE GENERATOR


def getteeth(
    origin,  # (x,y) of the starting point
    target,  # (x,y) of the target point
    teeth=3,  # Number of teeth (just protrusions, not all deformations)
    offset=1,  # Teeth depth, to the right from the direction origin->target
    even=False,  # Whether teeth begin with a trough instead of a tooth
):
    'Provide teeth geometry for box generator.'
    # Check if there is a trivial case
    if teeth <= 0: return ([origin, target])
    # Calculate geometry steps
    steps = teeth * 2 - 1  # Number of actual steps in the line
    stepxy = (target[0] - origin[0]) / steps, (target[1] - origin[1]) / steps
    angle = math.atan2(target[1] - origin[1], target[0] - origin[0])
    depth = math.cos(angle + math.pi / 2) * offset, math.sin(angle + math.pi / 2) * offset
    # Collected geometry, prepare collector
    vertices = []  # Collector of (x,y)
    vertices.append(origin)
    if not even:  # Usual case
        vertices.append((origin[0] + depth[0], origin[1] + depth[1]))

    # Generate steps
    for s in range(1, steps + 1):
        parity = bool(s % 2) != even  # Local determination of step
        if parity:
            vertices.append((origin[0] + s * stepxy[0] + depth[0],
                             origin[1] + s * stepxy[1] + depth[1]))
            vertices.append((origin[0] + s * stepxy[0],
                             origin[1] + s * stepxy[1]))
        else:
            vertices.append((origin[0] + s * stepxy[0],
                             origin[1] + s * stepxy[1]))
            if s < steps: vertices.append((origin[0] + s * stepxy[0] + depth[0],
                                           origin[1] + s * stepxy[1] + depth[1]))

    # Collected all together, just return the vertices
    return vertices


### Self-test
#############
if __name__ == '__main__':
    boxsvg(44, 36, 28, outfile='paneltest.svg')
