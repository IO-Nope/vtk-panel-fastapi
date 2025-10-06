import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import panel as pn
import vtk
from panel.pane import VTK
import utils
import io
import numpy as np
import math
global isDebug
isDebug = True



def Create_vtk_cone():
    cone_source = vtk.vtkConeSource()
    cone_source.SetHeight(1.0)
    cone_source.SetRadius(0.5)
    cone_source.SetResolution(32)
    cone_source.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cone_source.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    colors = vtk.vtkNamedColors()
    actor.GetProperty().SetColor(colors.GetColor3d("LimeGreen"))

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d("DarkSlateGray"))

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetOffScreenRendering(1) 
    
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    return render_window
def Create_vtk_sphere():
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(0.5)
    sphere_source.SetThetaResolution(32)
    sphere_source.SetPhiResolution(32)
    sphere_source.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere_source.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    colors = vtk.vtkNamedColors()
    actor.GetProperty().SetColor(colors.GetColor3d("Tomato"))

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d("DarkSlateGray"))

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetOffScreenRendering(1) 

    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    return render_window
def Create_vtk_cube():
    cube_source = vtk.vtkCubeSource()
    cube_source.SetXLength(1.0)
    cube_source.SetYLength(1.0)
    cube_source.SetZLength(1.0)
    cube_source.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube_source.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    colors = vtk.vtkNamedColors()
    actor.GetProperty().SetColor(colors.GetColor3d("CornflowerBlue"))

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d("DarkSlateGray"))

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetOffScreenRendering(1) 

    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    return render_window

def To_html(panel_app):
    html_buffer = io.StringIO()
    panel_app.save(html_buffer, embed=False)
    html_content = html_buffer.getvalue()
    html_buffer.close()
    return html_content

def Read_template(path="templates/index.html"):
    with open(path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

def hex_to_rgb(hex_color:str):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb_color:tuple):
    return '#%02x%02x%02x' % (int(rgb_color[0]*255), int(rgb_color[1]*255), int(rgb_color[2]*255))

def show_type(obj):
    print(type(obj))

def div_factor(n:int):
    return n+1/4*n

def Dprint(*args, **kwargs):
    if isDebug:
        print(*args, **kwargs)

def Choose_element_grid(n_elements:int,L:float,W:float,H:float):
    sum = L + W + H
    if sum == 0 or n_elements <= 0:
        return (1,1,1)
    factor = np.cbrt((n_elements-1)/(L*W*H))
    nx = math.floor(L*factor)
    ny = math.floor(W*factor)
    nz = math.floor(H*factor)
    return (max(1,nx),max(1,ny),max(1,nz))

def gen_mesh_from_elements(n_elements:int,L:float,W:float,H:float):
    nx_e,ny_e,nz_e = Choose_element_grid(n_elements,L,W,H)
    nx = nx_e + 1
    ny = ny_e + 1
    nz = nz_e + 1

    coords = []
    
    for k in range(nz):
        z = H * k / (nz - 1) if nz > 1 else 0
        for j in range(ny):
            y = W * j / (ny - 1) if ny > 1 else 0
            for i in range(nx):
                x = L * i / (nx - 1) if nx > 1 else 0
                coords.append((x, y, z))

    elements = []
    for k in range(nz_e):
        for j in range(ny_e):
            for i in range(nx_e):
                n0 = i + j * nx + k * nx * ny
                n1 = (i + 1) + j * nx + k * nx * ny
                n2 = (i + 1) + (j + 1) * nx + k * nx * ny
                n3 = i + (j + 1) * nx + k * nx * ny
                n4 = i + j * nx + (k + 1) * nx * ny
                n5 = (i + 1) + j * nx + (k + 1) * nx * ny
                n6 = (i + 1) + (j + 1) * nx + (k + 1) * nx * ny
                n7 = i + (j + 1) * nx + (k + 1) * nx * ny
                elements.append((n0, n1, n2, n3, n4, n5, n6, n7))
    return coords, elements
