'''Generate an SVG file from a given list.
I.e. give a list of a lists of vertices.
E.g. [[0,1,2,3],[3,4,5,6,7,8,9,10]]
...always in X-Y succession. If there are two points, use line, or use polyline
if three or more. If three numbers, it's a X-Y-R circle.
If color specified, add it as a color name as a last item in the list. [1,2,3,4,'blue'] for a 1,2-3,4 line

Return a text file that can be written out.

Warning! In comparison to original, ViewBox has been omitted
'''


def gensvg(vertices, filename = None, xoffset = 0, yoffset = 0):
    '''Main one, works as described above.
    If as a second parameter file with path is specified, it's saved there too.
    '''
    outfile = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<!-- Creator: Python_SVGGEN -->
<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" version="1.1" style="shape-rendering:geometricPrecision; text-rendering:geometricPrecision; image-rendering:optimizeQuality; fill-rule:evenodd; clip-rule:evenodd"
 xmlns:xlink="http://www.w3.org/1999/xlink">
 <defs>
  <style type="text/css">
   <![CDATA[
    .fil0 {fill:none}
   ]]>
  </style>
 </defs>
 <g id="Layer1">
'''

    for seg in vertices:
        loccolor = 'black'  # Which color is it?

        # Find if color is specified
        if type(seg[-1]) == str:
            loccolor = seg[-1]
            seg = seg[0:-1]

        # Process segment by segment
        if len(seg) == 3:
            # Circle
            outfile += '  <circle class="fil0" style="stroke:' + loccolor + ';" cx="{0}" cy="{1}" r="{2}" />\n'.format(seg[0] + xoffset, seg[1] + yoffset, seg[2])
            continue

        if len(seg) % 2:
            print('Warning! Odd number of vertices in GENSVG')
            continue  # Odd number of vertices, ignore!

        if len(seg) == 4:
            # Standard line
            outfile += ('  <line class="fil0" style="stroke:' + loccolor + ';" x1="{0}" y1="{1}" x2="{2}" y2= "{3}" />\n'.format(seg[0] + xoffset, seg[1] + yoffset, seg[2] + xoffset, seg[3] + yoffset))
        else:
            # Polyline
            outfile += '  <polyline class="fil0" style="stroke:' + loccolor + ';" points="'
            for p in range(0, len(seg), 2):
                outfile += '{0},{1} '.format(seg[p] + xoffset, seg[p + 1] + yoffset)
            outfile += '"/>\n'

    # Close up
    outfile += ' </g></svg>'

    # Export to file?
    if filename:
        fhand = open(filename, 'w')
        fhand.write(outfile)
        fhand.close()

    return outfile


# ## Self test
if __name__ == '__main__':
    print(gensvg([[1, 2, 3, 4], [5, 6, 7, 8, 9, 10, '#00FFFF'], [11, 12, 10, 'blue']], 'test.svg'))
