from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import panel as pn
import vtk
from panel.pane import VTK
import utils
import io

def create_vtk_cube():
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

    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    return render_window