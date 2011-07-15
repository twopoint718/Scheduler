import sys
#
# Drawing primitives (here be PostScript-specific dragons)
#
def render_preamble(rect, toFile=sys.stdout):
    """Emit the required boilerplate for a postscript document"""
    page_height = rect.max_y - rect.min_y
    print("""%%!PS-Adobe-2.0
%%%%BoundingBox: 0 0 612 %d
%%%%Creator: scheduler <cwilson@physics.wisc.edu>
%%%%Title: lab schedule
%%%%Pages: 1
%%%%PageOrder: Ascend
%%%%DocumentData: Clean7Bit
%%%%EndComments
%%%%BeginProlog
%%%%EndProlog
%%%%BeginSetup
<< /PageSize [612 %d] >> setpagedevice
%%%%EndSetup
%%%%Page: 1 1""" % (page_height, page_height), file=toFile)
    return

def render_footer(toFile=sys.stdout):
    """Emit the required trailing boilerplate for a postscript document"""
    print("showpage", file=toFile)
    print("%%Trailer", file=toFile)
    print("%%EOF", file=toFile)

def box(p1, p2, fill=False, color=1.0, toFile=sys.stdout):
    """Draw a basic rectangle with corners at p1 and p2.  Pretty much a
    low-level mapping of the Rectangle object"""
    w = p2.x - p1.x
    h = p2.y - p1.y
    lines = list()
    lines.append("%% BOX at %s %f by %f" % (p1, w, h))
    lines.append("%f %f moveto" % (p1.x, p1.y))
    lines.append("%f 0 rlineto" % w)
    lines.append("0 %f rlineto" % h)
    lines.append("%f 0 rlineto" % (-1.0*w))
    lines.append("0 %f rlineto" % (-1.0*h))
    if fill:
        lines.append("gsave closepath")
        lines.append("%0.2f setgray" % color)
        lines.append("fill")
        lines.append("0 setgray grestore")
    lines.append("closepath stroke")
    print("\n".join(lines), file=toFile)
    return lines

def text(pt, txt, font="Helvetica", size=12, center=True, toFile=sys.stdout):
    """Draw a line of PostScript text. Normally, code to center the line
    horizontally is emitted."""
    lines = list()
    lines.append("%% LABEL at %s (%s)" % (pt, txt))
    lines.append("%f %f moveto" % (pt.x, pt.y))
    lines.append("/%s findfont %f scalefont setfont" % (font, size))
    if center:
        lines.append("(%s) dup stringwidth pop 2 div neg 0 rmoveto show" % txt)
    else:
        lines.append("(%s) show" % txt)
    print("\n".join(lines), file=toFile)
    return lines

#
# drawing primitives SVG
#
def svg_render_preamble(rect, toFile=sys.stdout):
    lines = list()
    lines.append('<svg xmlns="http://www.w3.org/2000/svg" ' +
                 'width="%dpx" height="%dpx" ' % (rect.width, rect.height) +
                 'xmlns:xlink="http://www.w3.org/1999/xlink">')
    print("\n".join(lines), file=toFile)
    return lines

def svg_render_footer(toFile=sys.stdout):
    lines = list()
    lines.append('</svg>')
    print("\n".join(lines), file=toFile)
    return lines

def svg_box(p1, p2, fill=False, color=1.0, toFile=sys.stdout):
    lines = list()
    toHex = lambda x: "#" + ("%02x" % int(x * 255)) * 3
    width = p2.x - p1.x
    height = p2.y - p1.y
    l1 = '<rect x="%f" y="%f" height="%f" width="%f" style="stroke: %s; fill: %s;"/>' % \
        (p1.x, p1.y, height, width, toHex(0), toHex(color))
    lines.append(l1)
    print("\n".join(lines), file=toFile)
    return lines

def svg_text(pt, txt, font="Helvetica", size=12, center=True, toFile=sys.stdout):
    """Draw a line of SVG text. Normally code to center the line
    horizontally is emitted."""
    if center:
        anchorpos = "middle"
    else:
        anchorpos = "start"
    style = "font-family: '%s'; font-size: %dpt;" % (font, size)
    lines = list()
    lines.append('<text x="%f" y="%f" style="%s" text-anchor="%s">%s</text>' % \
                     (pt.x, pt.y, style, anchorpos, txt))
    print("\n".join(lines), file=toFile)
    return lines

def svg_text_multi(pt, txt, font="Helvetica", size=12, center=True,
                   toFile=sys.stdout):
    lines = list()
    if center:
        anchorpos = "middle"
    else:
        anchorpos = "start"

    # heading
    lines.extend(svg_text(pt, txt[0], "Helvetica", size+2, False, toFile))
    offset = 0
    for line in txt[1:]:
        offset = offset + size
        lines.extend(svg_text(pt.translate((0,offset)), line, "Helvetica",
                              size, False, toFile))
    print("\n".join(lines), file=toFile)
    return lines

def svg_hline(pt, length, toFile=sys.stdout):
    lines = list()
    lines.append('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:#000000;"/>' %\
                     (pt.x, pt.y, pt.x+length, pt.y))
    print("\n".join(lines), file=toFile)
    return lines
