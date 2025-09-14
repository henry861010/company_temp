import matplotlib.pyplot as plt
import klayout.db as pya
# install package "pip install klayout"

def polygons_to_region(polys_xy, dbu):
    """polys_xy: list of polygons, each polygon is list of (x,y) in microns"""
    reg = pya.Region()
    for poly in polys_xy:
        pts = [pya.Point(int(round(x / dbu)), int(round(y / dbu))) for (x, y) in poly]
        reg.insert(pya.Polygon(pts))
    return reg

def region_to_polygons(region, dbu):
    polygon_list = []
    for poly in region.each_merged():
        # Get hull points (clockwise) in µm
        hull = [(node.x*dbu, node.y*dbu) for node in poly.each_point_hull()]

        # Iterate each hole’s contour (counter-clockwise)
        holes = []
        for h in range(poly.holes()):
            holes.append([(node.x*dbu, node.y*dbu) for node in poly.each_point_hole(h)])
            
        ### append
        polygon_list.append((hull, holes))
    return polygon_list

def compute_gap_fill(dies_polys_xy, gap_um, chip_window_xy=None, dbu=0.001):
    """
    dies_polys_xy: [ [(x,y),...], [(x,y),...], ... ]  # die outlines in microns
    gap_um: float   # threshold distance (microns)
    chip_window_xy: optional polygon to confine fill (e.g., die field/bounding area)
    dbu: layout database unit in microns (0.001 = 1 nm)
    Returns: list of fill polygons (each a list of (x,y) microns)
    """
    # 1) Build regions for each die
    die_regs = []
    for poly in dies_polys_xy:
        die_regs.append(polygons_to_region([poly], dbu))

    # 2) Precompute a void/clip window (optional but recommended)
    #    If none given, use a loose bbox around all dies
    if chip_window_xy is None:
        # Compute bbox of all die regions and inflate it a bit
        all_die = pya.Region()
        for r in die_regs:
            all_die |= r
        bbox = all_die.bbox()
        pad = int(round((gap_um * 2) / dbu))
        chip_box = pya.Region(pya.Box(bbox.left - pad, bbox.bottom - pad,
                                      bbox.right + pad, bbox.top + pad))
    else:
        chip_box = polygons_to_region([chip_window_xy], dbu)

    # 3) Grow each die by gap/2
    r = int(round((gap_um / 2.0) / dbu))
    grown_regs = [rgn.sized(r, r) for rgn in die_regs]  # disk-like growth

    # 4) Pairwise overlaps of grown dies → candidate fill zones
    #    Restrict to the empty space by subtracting the original dies
    all_dies_union = pya.Region()
    for rgn in die_regs:
        all_dies_union |= rgn

    fill_accum = pya.Region()
    n = len(grown_regs)
    for i in range(n):
        gi = grown_regs[i]
        for j in range(i + 1, n):
            gj = grown_regs[j]
            overlap = gi & gj
            if overlap.is_empty():
                continue
            # Remove any area that lies inside the dies themselves
            overlap -= all_dies_union
            if overlap.is_empty():
                continue
            # Clip to chip window to avoid growth beyond design area
            overlap &= chip_box
            if not overlap.is_empty():
                fill_accum |= overlap

    # 5) Optional: simplify/merge and snap
    fill_accum.merge()
    return region_to_polygons(fill_accum, dbu)

# Example dies: two rectangles ~10 µm apart; gap_um = 15 will fill between them
dies = [
    [(0, 0), (10, 0), (10, 10), (0, 10)],
    [(15, 0), (25, 0), (25, 10), (15, 10)],
]
for die in dies:
    x, y = zip(*die)
    plt.fill(list(x)+[x[0]], list(y)+[y[0]], facecolor="lightgreen", edgecolor="black")
    
gap_um = 30.0  # fill only where separation < 30 µm
gap_list = compute_gap_fill(dies, gap_um)
for polygon in gap_list:
    hull, holes = polygon

    # Unzip into x, y lists
    x, y = zip(*hull)
    plt.fill(list(x)+[x[0]], list(y)+[y[0]], facecolor="lightblue", edgecolor="black")

plt.gca().set_aspect("equal")
plt.show()