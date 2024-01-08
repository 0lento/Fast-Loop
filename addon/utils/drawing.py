import bpy
import blf
import gpu

from gpu_extras.batch import batch_for_shader
from gpu_extras import presets
from struct import pack

from . import ui, common

COLOR_POINT = (1.0, 1.0, 0.0, 1)
COLOR_LINE = (0.5, 0.5, 1, 1)

def draw_point(point, color=(1.0, 1.0, 0.0, 1), size=3.0):
    draw_points([point], color=color, size=size)

def draw_points(points, color=(1.0, 1.0, 0.0, 1), size=3.0, occlude=True):
    ui_scale = ui.get_ui_scale()

    if common.prefs().occlude_points and occlude:
        gpu.state.depth_test_set('LESS_EQUAL')
   
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'POINTS', {"pos": points})
    shader.bind()
    shader.uniform_float("color", color)

    batch.draw(shader)

    gpu.state.depth_test_set('NONE')

def draw_line_loop(points, line_color=(0.0, 1.0, 0.5, 0.9), line_width=1.0):
    ui_scale = ui.get_ui_scale()
    r, g, b, a = line_color

    if common.prefs().occlude_lines:
        gpu.state.depth_test_set('LESS_EQUAL')

    gpu.state.blend_set('ALPHA') if a < 1 else gpu.state.blend_set('NONE')

    shader = gpu.shader.from_builtin('POLYLINE_SMOOTH_COLOR')
    batch = batch_for_shader(shader, 'LINE_LOOP', {"pos": points, "color": [line_color] * len(points)})
    
    shader.bind()
    shader.uniform_float("lineWidth", line_width * ui_scale)
    shader.uniform_float("viewportSize", (bpy.context.area.width, bpy.context.area.height))
    batch.draw(shader)

    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('NONE')

def draw_line(points, line_color=(0.0, 1.0, 0.5, 0.9), line_width=1.0):
    ui_scale = ui.get_ui_scale()
    a = line_color[3]

    if common.prefs().occlude_lines:
        gpu.state.depth_test_set('LESS_EQUAL')

    gpu.state.blend_set('ALPHA') if a < 1 else gpu.state.blend_set('NONE')

    shader = shader = gpu.shader.from_builtin('POLYLINE_SMOOTH_COLOR')
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points, "color": [line_color] * len(points)})
    
    shader.bind()
    shader.uniform_float("lineWidth", line_width * ui_scale)
    shader.uniform_float("viewportSize", (bpy.context.area.width, bpy.context.area.height))

    batch.draw(shader)

    gpu.state.depth_test_set('NONE')

def draw_lines(points, line_color=(0.0, 1.0, 0.5, 0.4), line_width=1.0):
    ui_scale = ui.get_ui_scale()
    shader = gpu.shader.from_builtin('POLYLINE_SMOOTH_COLOR')
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points, "color": [line_color] * len(points)})
    
    shader.bind()
    r, g, b, a = line_color

    if common.prefs().occlude_lines:
        gpu.state.depth_test_set('LESS_EQUAL')

    gpu.state.blend_set('ALPHA') if a < 1 else gpu.state.blend_set('NONE')

    shader.uniform_float("lineWidth", line_width * ui_scale)
    shader.uniform_float("viewportSize", (bpy.context.area.width, bpy.context.area.height))
    batch.draw(shader)

    gpu.state.depth_test_set('NONE')

def batch_from_points(points, type_, shader):
    return batch_for_shader(shader, type_, {"pos": points})

def draw_points_2d(points, color=(.0, 1.0, 0.0, 1), size=3.0):
    ui_scale = ui.get_ui_scale()
    
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'POINTS', {"pos": points})
    shader.bind()
    shader.uniform_float("color", color)

    batch.draw(shader)

def draw_line_2d(points, line_color=(0.0, 1.0, 0.5, 0.4), line_width=1.0):
    ui_scale = ui.get_ui_scale()

    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(line_width)

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_from_points(points, 'LINE_STRIP', shader)
    
    shader.bind()
    color = shader.uniform_from_name("color")
    r, g, b, a = line_color
    shader.uniform_vector_float(color, pack("4f", r, g, b, a), 4)
    batch.draw(shader)


from mathutils import Vector
def draw_rectangle_2d(size=10, center=(0,0)):
    size *= ui.get_ui_scale()
    bottom_left = Vector(center) + Vector((-1,-1)) * size
    bottom_right = Vector(center) + Vector((1,-1)) * size
    top_right = Vector(center) + Vector((1,1)) * size
    top_left = Vector(center) + Vector((-1,1)) * size
    vertices = (top_left, top_right, bottom_right, bottom_left)


    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINE_LOOP', {"pos": vertices})


    shader.bind()
    shader.uniform_float("color", (1, 1, 1, 1.0))
    batch.draw(shader)

def draw_circle_2d(center, radius, color=(1,1,1,1)):
    ui_scale = ui.get_ui_scale()
    presets.draw_circle_2d(center, color, radius * ui_scale)



def draw_region_border(context, line_color=(1, 1, 1, 1), width=2, text="Selection"):
    region = context.region
    scale = ui.get_ui_scale()
    width *= scale
    header_height = ui.get_header_height()
    top_left = Vector((width, region.height - (width + header_height)))
    top_right = Vector((region.width - width, region.height - (width + header_height)))
    bottom_right = Vector((region.width - width, width))
    bottom_left = Vector((width, width))
    vertices = (top_left, top_right, bottom_right, bottom_left,)

    gpu.state.line_width_set(width)

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    shader.bind()

    shader.uniform_float("color", line_color)

    batch = batch_for_shader(shader, 'LINE_LOOP', {"pos": vertices})
    batch.draw(shader)

    if text:

        font_size = int(16 * scale)

        blf.size(0, font_size, 72)
        blf.color(0, *line_color)

        center = (region.width) / 2 - 20
        blf.position(0, center - int(60 * scale), region.height - header_height - int(font_size) - 5, 0)

        blf.draw(0, text)

