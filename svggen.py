'''
SVGGEN v2
Lib for quick SVG generation from just a list of coordinates and colors.

Example: of a line and a circle (circle always has 3 coordinates, X-Y-R)
svggen([[1,2,3,4,'blue','fill:red'],[5,6,7,'yellow'],...]
(line from 1,2 to 3,4 in blue, then circle at (5,6) with radius 7 yellow)

Example text:
svggen([[20,0,1,1,'font:vectorfonts\\roman.svf','text:MADE IN CANADA']],'canada.svg')
(x,y,sizeX,sizeY,font definition file,actual label)

Example colored circle:
svggen([[11, 12, 5, 'blue', 'stroke-width:2', 'fill:red']])
(x,y,radius,color,stroke,fill)
'''

# CONSTANTS

HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<!-- Creator: Python_SVGGEN2 --><svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{fullwidth}mm" height="{fullheight}mm" version="1.1" style="shape-rendering:geometricPrecision; text-rendering:geometricPrecision; image-rendering:optimizeQuality; fill-rule:evenodd; clip-rule:evenodd" viewBox="{mmleft} {mmtop} {mmwidth} {mmheight}"
 xmlns:xlink="http://www.w3.org/1999/xlink"><g id="Layer1">
'''
FOOTER = '</g></svg>'

CIRCLETEMPLATE = '  <circle {3} cx="{0}" cy="{1}" r="{2}" />\n'
SIMPLELINETEMPLATE = '  <line {4} x1="{0}" y1="{1}" x2="{2}" y2="{3}" />\n'
POLYLINETEMPLATE1 = '  <polyline {0} points="'
POLYLINETEMPLATE2 = '" />\n'
POLYGONTEMPLATE1 = '  <polygon {0} points="'
POLYGONTEMPLATE2 = '" />\n'

# Get parameter string from dictionary


def getparamstring(parameters):
    '''Simply gets a parameter string from a dictionary for SVG XML.'''
    parstring = []
    for key in parameters.keys():
        parstring.append(str(key) + '="' + str(parameters[key]) + '"')
    parstring = ' '.join(parstring)
    return parstring

# Helper vector font parser


def parsevfont(filename):
    '''
    Gets a filename of vector font file and returns a dictionary
    with geometry.
    '''
    fontgeo = dict()  # Master collector

    # Load file
    inp = open(filename, 'r', encoding='utf8')
    ind = [e.strip('\n ') for e in inp.readlines() if e]
    inp.close()

    curchar = ' '  # Currently applied character
    # Parse line-by-line
    for line in ind:
        # Check if a designator or geometry
        if line.endswith(':'):
            curchar = line[0]
            if curchar not in fontgeo.keys():
                fontgeo[curchar] = []
            continue
        # Geometry
        if line.count(',') >= 2:
            # Split points
            points = [e for e in line.split(' ') if e]
            # Get numbers
            points = [[eval(v) for v in e.split(',')] for e in points]
            # Add to corresponding character
            fontgeo[curchar].append(points)

    # Collected all geometry; return
    return fontgeo

# Helper text generator


def genvectortext(values, params):
    '''
    values=[leftx,topy,zoomx,zoomy,letterspacing,linespacing,spacewidth]
    params={'text':'string','font':'somefont.svf'}
    Return a SVG snip, and the list of all points [(x,y),(x,y),...]
    '''
    # Load and parse font file
    fontvec = parsevfont(params['font'])

    # Set defaults if not supplied
    defaults = [None, None, 1, 1, 1, 7, 3]
    values = values + defaults[len(values):]  # attach
    # ...in order leftx,topy,zoomx,zoomy,letterspacing,linespacing,spacewidth
    # Localparse to variables
    origin = values[0], values[1]
    zoom = values[2], values[3]

    textgeo = []  # Collector of all lines
    allpoints = []  # Collector of all points at the end
    currentx, currenty = origin  # Work position

    # Iterate letter by letter to produce geometry
    for char in params['text']:
        # Firstly deal with special characters, before validation
        if char == '\n':
            # New line
            currentx = origin[0]
            currenty += values[5] * zoom[1]
            continue
        if char == ' ':
            # Space
            currentx += values[6] * zoom[0]
            continue
        if char not in fontvec.keys(): continue  # Unsupported character
        charwidth = 0  # Counter for later spacing calculations
        # Draw char at currentx,currenty
        chargeom = fontvec[char]
        for subline in chargeom:
            subl = []
            for cx, cy in subline:
                subl.append([currentx + cx * zoom[0], currenty + cy * zoom[1]])
                charwidth = max([charwidth, currentx + cx * zoom[0]])
            textgeo.append(subl)  # Key addition to master text geometry
        # Character drawn, now continue spacing
        currentx = charwidth + values[4] * zoom[0]

    # Geometry calculated for all characters in SVGGEN format, return it
    return textgeo

# Helper color parser


def colorparse(color):
    if color.count(',') == 2:  # r,g,b values
        rgb = color.split(',')
        r, g, b = [int(e) for e in rgb]
        return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)
    return color  # Not r,g,b so just return what supplied


# MAIN FUNCTION


def svggen(
    vertices,  # List of lists of coordinates and parameters
    filename=None,  # If given, a filename to write the SVG to
    xoffset=0,  # Offset of the entire SVG horizontally
    yoffset=0,  # Offset of the entire SVG vertically
    zoom=1,  # Multiplier of all coordinates (thus, a zoomer)
    window=None,  # x,y of viewport/scale. Subjected to zoom & offset
    # Default colors and widths to be set on the SVG level:
    linewidth=1,
    fill='none',
    linecolor='black',
    autoclosepoly=True,  # Automatically detect and convert closed paths to polygons
):
    # Set SVG defaults
    DEFAULTCOLOR = linecolor  # Can be any CSS color or a #rrggbb hex
    DEFAULTFILL = fill  # Typically none but can be changed to standard colors
    DEFAULTLINEWIDTH = linewidth  # Just a standard default != 0
    # Set up master viewport collector for final statistics
    viewport = []
    # Master geometry string collector to be appended to the final SVG
    svg = []

    # Master iterate over each individual list
    for shape in vertices:
        parameters = dict()  # Collector of stroke, fill and other parameters
        # Set defaults
        parameters['fill'] = DEFAULTFILL
        parameters['stroke'] = DEFAULTCOLOR
        parameters['stroke-width'] = DEFAULTLINEWIDTH
        dellist = []  # ID's to be deleted later
        # A workflow of checks and decisions
        # Look for a specifier in form 'parameter:value'
        for id in range(len(shape)):  # Iterate to find parameters
            if not isinstance(shape[id], str): continue  # Uninteresting if not a string
            param = shape[id]
            dellist.append(id)
            # Process it
            if ':' not in param:
                # If no parameter name, for backward compatibility assume stroke
                param = 'stroke:' + param
            # Split
            pname, tmp, pvalue = param.partition(':')
            # If a color, process the color
            if pname.lower() in ['stroke', 'fill']:
                pvalue = colorparse(pvalue)
            # Add it to the parameter dictionary
            parameters[pname] = pvalue
        # Assemble a parameter string
        parstring = getparamstring(parameters)
        # Clean up the shape from string-tags
        for id in reversed(dellist):
            del shape[id]

        # Processing choice of elements

        # Check if a text
        if 'text' in parameters.keys():
            # Relay to outside function
            textvec = genvectortext(shape, parameters)
            # Collect points
            textport = []
            for subline in textvec:
                for point in subline:
                    textport.append(point)
            viewport.extend(textport)
            # Reassemble parameter string
            del parameters['text']
            del parameters['font']
            parstring = getparamstring(parameters)
            # Now create and parse
            for subline in textvec:
                if len(subline) == 2:
                    # Simple x-y Line
                    svg.append(SIMPLELINETEMPLATE.format(
                        subline[0][0], subline[0][1],
                        subline[1][0], subline[1][1], parstring))
                else:
                    # Polyline
                    segs = []  # Mini-collector
                    for px, py in subline:
                        segs.append(str(px) + ',' + str(py))
                    segs = ' '.join(segs)
                    # Combined all coordinates
                    svg.append(POLYLINETEMPLATE1.format(parstring) +
                               segs + POLYLINETEMPLATE2)
            continue

        # Check if it is a circle (3 coordinates)
        if len(shape) == 3 and not isinstance(shape[0], list) and \
                not isinstance(shape[0], tuple):
            # Circle as X, Y, R
            cx, cy, cr = shape
            # Perform transformations
            cx = cx * zoom + xoffset
            cy = cy * zoom + yoffset
            cr = cr * zoom
            # Add to collectors
            svg.append(CIRCLETEMPLATE.format(cx, cy, cr, parstring))
            viewport.append((cx - cr, cy - cr))
            viewport.append((cx + cr, cy + cr))
            continue

        # Flatten out if needed
        if isinstance(shape[0], list) or isinstance(shape[0], tuple):
            # Indeed, flatten it
            collector = []
            [collector.extend([x, y]) for x, y in shape]
            shape = collector

        # Check number of vertices
        if len(shape) % 2:
            print('Shape has odd number of vertex coordinates! Skipping', shape)
            continue

        # Straight simple line
        if len(shape) == 4:
            # Extract vertices
            shape = [shape[0] * zoom + xoffset, shape[1] * zoom + yoffset,
                     shape[2] * zoom + xoffset, shape[3] * zoom + yoffset]
            # Add to collectors
            svg.append(SIMPLELINETEMPLATE.format(*shape, parstring))
            viewport.append((shape[0], shape[1]))
            viewport.append((shape[2], shape[3]))
            continue

        # The only remaining option: polygon or polyline
        coordlist = []  # Local collector
        # Check if closed (polygon), i.e. first point==last point
        polygon = False
        if shape[0] == shape[-2] and shape[1] == shape[-1] and autoclosepoly:
            # Indeed a closed polygon
            polygon = True
            shape = shape[:-2]
        # Iterate over all coordinates
        for p in range(0, len(shape), 2):
            # Extract vertices
            cx = shape[p] * zoom + xoffset
            cy = shape[p + 1] * zoom + yoffset
            # Add to collectors
            viewport.append((cx, cy))
            coordlist.append(str(cx) + ',' + str(cy))
        coordlist = ' '.join(coordlist)
        # Assemble polyline
        if polygon:
            final = POLYGONTEMPLATE1.format(parstring) + \
                coordlist + POLYGONTEMPLATE2
        else:
            final = POLYLINETEMPLATE1.format(parstring) + \
                coordlist + POLYLINETEMPLATE2
        svg.append(final)

    # Iterating finished. Collect coordinate extremes for viewport
    if window:
        # User-supplied
        if len(window) == 2:
            maxx = str(window[0] * zoom + xoffset)
            maxy = str(window[1] * zoom + yoffset)
            minx = str(xoffset)
            miny = str(yoffset)
        elif len(window) == 4:
            minx = str(window[0] * zoom + xoffset)
            miny = str(window[1] * zoom + xoffset)
            maxx = str(window[2] * zoom + xoffset)
            maxy = str(window[3] * zoom + xoffset)
    else:
        # Auto-calculated
        xpos = [c[0] for c in viewport]
        ypos = [c[1] for c in viewport]
        maxx = str(max(xpos))
        maxy = str(max(ypos))
        minx = min(xpos)
        miny = min(ypos)
        # Even if the minimums are >0, let them be 0
        if minx > 0: minx = 0
        if miny > 0: miny = 0
        minx = str(minx)
        miny = str(miny)
        fullwidth = maxx  # str(max(xpos) - min(xpos))
        fullheight = maxy  # str(max(ypos) - min(ypos))

    # Assemble final SVG. Firstly format header
    seg1 = HEADER.replace('{mmwidth}', maxx)
    seg1 = seg1.replace('{mmheight}', maxy)
    seg1 = seg1.replace('{mmleft}', minx)
    seg1 = seg1.replace('{mmtop}', miny)
    seg1 = seg1.replace('{fullwidth}', fullwidth)
    seg1 = seg1.replace('{fullheight}', fullheight)
    seg2 = ''.join(svg)
    seg3 = FOOTER
    finalsvg = seg1 + seg2 + seg3

    # Save to disk if needed
    if filename:
        outf = open(filename, 'w')
        outf.write(finalsvg)
        outf.close()

    # All done
    return finalsvg


# Self-test
#############
if __name__ == '__main__':
    print(svggen([[11, 12, 5, 'blue', 'stroke-width:2'],
                  [1, 2, 3, 4, '255,0,255'],
                  [[5, 6], [10, 8], [9, 10], '#00FFFF'],
                  [14, 15, 17, 16, 18, 18, 'fill:red', 13, 21, 14, 15, '#3377FF'],
                  [2, 2, 1, 1, 'text:Roman:At Blackett Strait,\nSolomons',
                      'font:vectorfonts\\roman.svf', '#ff0000', 'stroke-width:0.2'],
                  [2, 18, 1 / 2, 1 / 3, 1, 9, 3, 'text:classic2x3 ABCDEFGHIJKLMNOPQRSTUVWXYZ\n'
                   + 'abcdefghijklmnopqrstuvwxyz\n0123456789 '
                   + 'šđžčćŠĐŽČĆ\n?= /\\*-!+(),.:"# $%&[;]{}@<_>',
                   'font:vectorfonts\\roman.svf', 'stroke-width:0.1'],
                  ], 'test.svg'))
    svggen([[20, 0, 1, 1, 'font:vectorfonts\\roman.svf', 'text:MADE IN CANADA']], 'canada.svg')
    svggen([[3, 3, .3, .3, 'font:vectorfonts\\roman.svf', 'text:521307']], 'label.svg')
