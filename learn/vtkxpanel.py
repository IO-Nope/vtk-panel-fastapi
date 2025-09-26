import vtk
import panel as pn
from panel.pane import VTK

# init

pn.extension('vtk')

cube = vtk.vtkCubeSource()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cube.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

vtk_pane = VTK(render_window)

pn.Column("# 立方体展示", vtk_pane).servable()