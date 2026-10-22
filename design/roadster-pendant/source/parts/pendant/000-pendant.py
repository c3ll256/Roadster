from math import sin, cos, acos, sqrt, pi
length = param('pendant_length', 64.0)
height = param('pendant_height', 36.0)
thickness = param('pendant_thickness', 3.5)
corner = param('pendant_corner_radius', 3.0)
relief = param('pendant_relief_height', 0.6)
text_top_round = param('pendant_text_top_edge_radius', 0.45)
border_inset = param('pendant_border_inset', 0.7)
border_color_width = param('pendant_border_color_width', 0.7)
border_color_depth = param('pendant_border_color_depth', 0.6)
groove_depth = param('pendant_groove_depth', 0.45)
outer_radius = param('pendant_groove_outer_radius', 0.35)
bottom_radius = param('pendant_groove_bottom_radius', 0.45)
inner_radius = param('pendant_groove_inner_radius', 1.2)
text_width = param('pendant_text_width', 42.14)
text_height = param('pendant_text_height', 15.5)
text_y = param('pendant_text_center_y', -3.8)
header_height = param('pendant_header_height', 5.5)
header_y = param('pendant_header_center_y', 9.6)
header_relief = param('pendant_header_relief_height', 0.4)
letter_gap = param('pendant_letter_gap', 0.8379121789560895)
eye_od = param('pendant_eye_outer_diameter', 10.0)
eye_id = param('pendant_cord_hole_diameter', 4.0)
eye_offset = param('pendant_eye_outward_offset', 2.0)
eye_root_radius = param('pendant_eye_root_radius', 2.0)
recess_diameter = param('pendant_corner_recess_diameter', 1.8)
recess_depth = param('pendant_corner_recess_depth', 0.5)
recess_x = param('pendant_corner_recess_center_x', 26.0)
recess_y = param('pendant_corner_recess_center_y', 13.5)
# One integral plate, R3 plan corners, and left cord eye.
eye_x = -length/2-eye_offset
outline = RectangleRounded(length, height, corner) + Pos(eye_x,0)*Circle(eye_od/2)
# eye_root_transition reference: fill the two concave plan corners with tangent arcs.
root_y = sqrt((eye_od/2)**2-eye_offset**2)
root_vertices = [v for v in outline.vertices()
 if abs(v.X+length/2)<1e-6 and abs(abs(v.Y)-root_y)<1e-6]
assert len(root_vertices)==2, 'Expected the two ring-to-plate root corners'
outline = fillet(root_vertices, radius=eye_root_radius)
body = extrude(outline-Pos(eye_x,0)*Circle(eye_id/2), amount=thickness)

# Four tangent true circular arcs form a recessed asymmetric U.
# The large inner R1.2 eases gently onto the central field; the outer lip is R0.35.
theta = acos(1-groove_depth/(outer_radius+bottom_radius))
phi = acos(1-groove_depth/(inner_radius+bottom_radius))
outer_run = (outer_radius+bottom_radius)*sin(theta)
inner_run = (inner_radius+bottom_radius)*sin(phi)
groove_width = outer_run+inner_run
hx, hy = length/2-border_inset, height/2-border_inset
pr = corner-border_inset
assert pr > groove_width, 'Groove must fit inside plan corner radius'
assert thickness > groove_depth
# Closed CCW path begins at the midpoint of the lower edge, tangent +X.
q = sqrt(2)
path_edges = [
 Line((0,-hy,0),(hx-pr,-hy,0)).edge(),
 ThreePointArc((hx-pr,-hy,0),(hx-pr+pr/q,-hy+pr-pr/q,0),(hx,-hy+pr,0)).edge(),
 Line((hx,-hy+pr,0),(hx,hy-pr,0)).edge(),
 ThreePointArc((hx,hy-pr,0),(hx-pr+pr/q,hy-pr+pr/q,0),(hx-pr,hy,0)).edge(),
 Line((hx-pr,hy,0),(-hx+pr,hy,0)).edge(),
 ThreePointArc((-hx+pr,hy,0),(-hx+pr-pr/q,hy-pr+pr/q,0),(-hx,hy-pr,0)).edge(),
 Line((-hx,hy-pr,0),(-hx,-hy+pr,0)).edge(),
 ThreePointArc((-hx,-hy+pr,0),(-hx+pr-pr/q,-hy+pr-pr/q,0),(-hx+pr,-hy,0)).edge(),
 Line((-hx+pr,-hy,0),(0,-hy,0)).edge()
]
path_wire = Wire(path_edges)
arc_specs = [
 ((0,thickness-outer_radius), outer_radius, pi/2, pi/2-theta),
 ((outer_run,thickness-groove_depth+bottom_radius), bottom_radius, -pi/2-theta, -pi/2),
 ((outer_run,thickness-groove_depth+bottom_radius), bottom_radius, -pi/2, -pi/2+phi),
 ((groove_width,thickness-inner_radius), inner_radius, pi/2+phi, pi/2)
]
def section_point(center, radius, angle):
 return (0,-hy+center[0]+radius*cos(angle),center[1]+radius*sin(angle))
profile_edges = []
for center, radius, a0, a1 in arc_specs:
 profile_edges.append(ThreePointArc(section_point(center,radius,a0),section_point(center,radius,(a0+a1)/2),section_point(center,radius,a1)).edge())
p_outer = (0,-hy,thickness)
p_inner = (0,-hy+groove_width,thickness)
profile_edges += [
 Line(p_inner,(0,p_inner[1],thickness+1)).edge(),
 Line((0,p_inner[1],thickness+1),(0,-hy,thickness+1)).edge(),
 Line((0,-hy,thickness+1),p_outer).edge()
]
groove_cutter = sweep(Face(Wire(profile_edges)), path=path_wire, is_frenet=False)
body = body-groove_cutter
# Cosmetic flat-bottom blind holes, mirrored from the user's upper-left mark.
# Mark centre is approximately (-26,13.5,3.5); diameter is a disclosed default.
recess_centers = [(sx*recess_x,sy*recess_y) for sx in (-1,1) for sy in (-1,1)]
assert 0 < recess_depth < thickness
assert recess_x+recess_diameter/2 < length/2-border_inset-groove_width
assert recess_y+recess_diameter/2 < height/2-border_inset-groove_width
for x,y in recess_centers:
 body = body-Pos(x,y,thickness-recess_depth)*Cylinder(recess_diameter/2,recess_depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
print('Four blind holes:',recess_centers,'diameter/depth mm:',recess_diameter,recess_depth,
 'remaining floor mm:',thickness-recess_depth)

# rdstr_lettering: user supplied 1774x887 black-on-white image.
# Outlines are redrawn in source-pixel coordinates; shading is not part of the silhouette.
# Pixel bounds of the five components: R 284..515, D 537..758,
# S 793..1012, T 1029..1237, R 1259..1491, global Y 218..662.
R_outer = [('M',(0,661)),('L',(0,219)),('L',(154,219)),
 ('B',(195,219),(218,244),(218,285)),('L',(218,394)),
 ('B',(218,432),(202,451),(171,461)),
 ('L',(231,661)),('L',(151,661)),('L',(90,465)),('L',(81,465)),
 ('L',(81,661)),('L',(0,661))]
R_inner = [('M',(81,270)),('L',(117,270)),
 ('B',(132,270),(137,277),(137,291)),('L',(137,395)),
 ('B',(137,410),(132,415),(117,415)),('L',(81,415)),('L',(81,270))]
D_outer = [('M',(0,661)),('L',(0,219)),('L',(157,219)),
 ('B',(198,219),(221,244),(221,285)),('L',(221,595)),
 ('B',(221,637),(198,661),(157,661)),('L',(0,661))]
D_inner = [('M',(81,270)),('L',(117,270)),
 ('B',(132,270),(137,277),(137,291)),('L',(137,591)),
 ('B',(137,605),(132,611),(117,611)),('L',(81,611)),('L',(81,270))]
S_outer = [('M',(219,336)),('L',(138,336)),('L',(138,288)),
 ('B',(138,274),(132,268),(117,268)),('L',(108,268)),
 ('B',(93,268),(88,275),(88,290)),('L',(88,327)),
 ('B',(88,348),(93,365),(107,381)),('L',(188,476)),
 ('B',(208,500),(219,521),(219,549)),('L',(219,591)),
 ('B',(219,638),(195,662),(151,662)),('L',(69,662)),
 ('B',(24,662),(0,637),(0,593)),('L',(0,533)),('L',(82,533)),('L',(82,591)),
 ('B',(82,607),(88,613),(103,613)),('L',(114,613)),
 ('B',(129,613),(135,607),(135,592)),('L',(135,555)),
 ('B',(135,535),(130,520),(115,503)),('L',(35,410)),
 ('B',(12,383),(4,359),(4,328)),('L',(4,287)),
 ('B',(4,244),(28,218),(71,218)),('L',(151,218)),
 ('B',(195,218),(219,244),(219,287)),('L',(219,336))]
T_outer = [('M',(0,219)),('L',(208,219)),('L',(208,270)),
 ('L',(145,270)),('L',(145,661)),('L',(61,661)),('L',(61,270)),
 ('L',(0,270)),('L',(0,219))]
def outline_face(commands, source_width, modeled_width):
 edges = []
 current = None
 def v(p):
  return (p[0]/source_width*modeled_width,(440-p[1])/444*text_height,0)
 for command in commands:
  if command[0] == 'M':
   current = v(command[1])
  elif command[0] == 'L':
   end = v(command[1])
   edges.append(Line(current,end).edge())
   current = end
  else:
   c1,c2,end = [v(p) for p in command[1:]]
   edges.append(Bezier(current,c1,c2,end).edge())
   current = end
 return Face(Wire(edges))
# Keep photographed optical gaps in their measured ratio; letter_gap is their mean.
glyph_outlines = [
 (R_outer,R_inner,231,231),(D_outer,D_inner,221,221),
 (S_outer,None,219,219),(T_outer,None,208,208),(R_outer,R_inner,231,232)]
source_gaps = [22,35,17,22]
glyph_scale = (text_width-4*letter_gap)/1111
cursor = -text_width/2
glyph_bounds = []
glyph_solids = []
for i,(outer,inner,source_width,layout_width) in enumerate(glyph_outlines):
 gw = layout_width*glyph_scale
 glyph = outline_face(outer,source_width,gw)
 if inner is not None:
  glyph = glyph-outline_face(inner,source_width,gw)
 raised = Pos(cursor,text_y,thickness)*extrude(glyph,amount=relief,dir=(0,0,1))
 glyph_bounds.append(raised.bounding_box())
 top_z = thickness+relief
 top_edges = [e for e in raised.edges()
  if abs(e.bounding_box().min.Z-top_z)<1e-6 and abs(e.bounding_box().max.Z-top_z)<1e-6]
 glyph_solids.append(fillet(top_edges,radius=text_top_round).solids()[0])
 cursor += gw
 if i<4:
  cursor += source_gaps[i]/24*letter_gap
actual_text_width = max(b.max.X for b in glyph_bounds)-min(b.min.X for b in glyph_bounds)
actual_text_height = max(b.max.Y for b in glyph_bounds)-min(b.min.Y for b in glyph_bounds)
assert abs(actual_text_width-text_width)<1e-5
assert abs(actual_text_height-text_height)<1e-5
print('Measured lettering footprint mm:',actual_text_width,actual_text_height)
# Script heading: inclined brush lettering, matching the supplied California style.
# Exact available font face; fail rather than silently use a sans-serif fallback.
script_font = 'Brush Script MT Italic'
assert script_font in [f.name for f in available_fonts()], 'Brush script font is required'
header_sketch = Text('Hangzhou',10,font=script_font)
header_sketch = header_sketch.scale(header_height/header_sketch.bounding_box().size.Y)
hb = header_sketch.bounding_box()
header_sketch = Pos(-(hb.min.X+hb.max.X)/2,header_y-(hb.min.Y+hb.max.Y)/2)*header_sketch
header_raw = Pos(0,0,thickness)*extrude(header_sketch,amount=header_relief)
header_solids = list(header_raw.solids())
# Four non-overlapping material objects, all co-printed on the plate.
assert 0 < border_color_width <= border_inset
assert 0 < border_color_depth < thickness
border_profile = (RectangleRounded(length,height,corner)
 - RectangleRounded(length-2*border_color_width,height-2*border_color_width,corner-border_color_width))
border = (Pos(0,0,thickness-border_color_depth)*extrude(border_profile,amount=border_color_depth)).solids()[0]
silver_body = (body-border).solids()[0]
navy = srgb('#17365d')
red = srgb('#d51f2a')
silver_body.color = srgb('#bfc1c4')
border.color = navy
for glyph in glyph_solids:
 glyph.color = navy
for glyph in header_solids:
 glyph.color = red
rdstr = Compound(children=glyph_solids)
rdstr.color = navy
hangzhou = Compound(children=header_solids)
hangzhou.color = red
combined = silver_body+border
for glyph in glyph_solids+header_solids:
 combined = combined+glyph
assert len(combined.solids())==1 and combined.is_valid, 'Co-printed pendant must be continuous'
assert all(g.is_valid for g in [silver_body,border]+glyph_solids+header_solids)
summed_volume = silver_body.volume+border.volume+sum(s.volume for s in glyph_solids+header_solids)
assert abs(summed_volume-combined.volume)<1e-5, 'Material regions must not overlap'
main_top = max(b.max.Y for b in glyph_bounds)
header_bottom = header_sketch.bounding_box().min.Y
assert header_bottom>main_top, 'Two text rows must remain separated'
field_hx = length/2-border_inset-groove_width
field_hy = height/2-border_inset-groove_width
assert max(abs(header_sketch.bounding_box().min.X),abs(header_sketch.bounding_box().max.X))<field_hx
assert header_sketch.bounding_box().max.Y<field_hy
print('RDSTR size mm:',actual_text_width,actual_text_height,'center Y:',text_y)
print('Hangzhou size mm:',header_sketch.bounding_box().size,'center Y:',header_y)
print('Row gap mm:',header_bottom-main_top)
print('Inner-field clearances mm: LR',(length-actual_text_width)/2-border_inset-groove_width,
 'bottom',min(b.min.Y for b in glyph_bounds)+field_hy,
 'header top',field_hy-header_sketch.bounding_box().max.Y)
print('Overall mm:',combined.bounding_box().size,'connected solids:',len(combined.solids()))
publish('pendant',silver_body,'银灰车牌主体',material='petg')
publish('border',border,'深蓝车牌细边',material='petg')
publish('rdstr',rdstr,'深蓝 RDSTR',material='petg')
publish('hangzhou',hangzhou,'红色手写 Hangzhou',material='petg')
