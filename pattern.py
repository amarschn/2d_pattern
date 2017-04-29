import math
from mecode import G

g = G(
    aerotech_include=False,
    print_lines=False,
    extrude=True,
    outfile='./pattern.gcode',
    layer_height = 0.6,
    extrusion_width = 0.84,
    filament_diameter = 1.75,
    extrusion_multiplier = 1
)


# Width and height of overall pattern. Actual pattern will be slightly bigger as
# the segments are not truncated.
width = 300
height = 300

# Extra spacing to add between the vertical passes. This should be used to
# account for filament width to prevent overlap if not desired.
spacing = 0.1

# The length and angle of the straight sections of the repeating pattern.
straight_length = 10
straight_angle = 45

# Whether or not to add rounded corners. corner_radius is only used if True
round_corners = False
corner_radius = 5

# If round_corners are not enabled this is the length of the straight segment
# used instead.
connection_length = 20

# Add an additional y offset between adjacent passes.
offset = True


# GCode to insert at the beginning and end of the print.
preamble = """
G28
G29
M236 S17
G1 F900
G90
G1 Z10
G1 X85 Y25
G1 Z0.2
G91
M400
M42 P8 S255
G4 S0.6
"""
postamble = """
M400
M42 P8 S0
G1 Z10
"""


straight_x = math.cos(straight_angle * math.pi / 180) * straight_length
straight_y = math.sin(straight_angle * math.pi / 180) * straight_length

x_loops = int(math.ceil(width / (straight_x + spacing)))
if round_corners:
    x_loops = int(math.ceil(width / (straight_x + spacing + corner_radius)))
    y_loops = int(math.ceil(height / (straight_y + 2*corner_radius)))
else:
    x_loops = int(math.ceil(width / (straight_x + spacing)))
    y_loops = int(math.ceil(height / (straight_y + connection_length)))

xdir = 1
ydir = 1

[g.write(line) for line in preamble.split('\n')]
for xi in range(x_loops):
    for yi in range(y_loops):
        g.move(straight_x*xdir, straight_y*ydir)
        if (not yi == y_loops - 1) or offset:
            if round_corners:
                if ydir > 0:
                    direction = 'CCW' if (xdir > 0) else 'CW'
                else:
                    direction = 'CW' if (xdir > 0) else 'CCW'
                g.arc(x=0, y=corner_radius*2*ydir, direction=direction)
            else:
                g.move(y=connection_length*ydir)
        xdir *= -1
    if xi != x_loops - 1:  # don't jog if there is not another line
        xjog = spacing
        if round_corners:
            xjog += corner_radius
        if xdir == 1:
            xjog += 2*straight_x
        g.move(x=xjog)
    ydir *= -1
    xdir *= -1
[g.write(line) for line in postamble.split('\n')]


g.view('matplotlib')
g.teardown()
