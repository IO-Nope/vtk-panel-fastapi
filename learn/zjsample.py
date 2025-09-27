import numpy as np
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, vtkPoints, vtkCellArray, vtkTriangle
from vtkmodules.vtkCommonCore import vtkFloatArray
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor, vtkActor, vtkDataSetMapper

# 1. 定义简支梁的参数
length = 10.0  # 梁的长度（单位：m）
height = 0.5   # 梁的高度（单位：m）
E = 210e9      # 弹性模量（单位：Pa）
I = (height**3) / 12  # 截面惯性矩（矩形截面）
q = 10000      # 均布载荷（单位：N/m）

# 2. 离散化梁（有限元网格）
num_elements = 20  # 单元数量
num_nodes = num_elements + 1
node_coords = np.linspace(0, length, num_nodes)  # 节点坐标
element_length = length / num_elements

# 3. 组装刚度矩阵
K = np.zeros((num_nodes, num_nodes))  # 全局刚度矩阵
F = np.zeros(num_nodes)               # 力向量

for i in range(num_elements):
    k_local = (E * I / element_length**3) * np.array([
        [12, 6*element_length, -12, 6*element_length],
        [6*element_length, 4*element_length**2, -6*element_length, 2*element_length**2],
        [-12, -6*element_length, 12, -6*element_length],
        [6*element_length, 2*element_length**2, -6*element_length, 4*element_length**2]
    ])
    # 将局部刚度矩阵添加到全局刚度矩阵
    dof = [i, i+1]
    for a in range(2):
        for b in range(2):
            K[dof[a], dof[b]] += k_local[a, b]

# 4. 应用边界条件（简支梁）
K[0, :] = 0
K[:, 0] = 0
K[-1, :] = 0
K[:, -1] = 0
K[0, 0] = 1
K[-1, -1] = 1

# 5. 施加载荷
for i in range(1, num_nodes-1):
    F[i] = -q * element_length

# 6. 求解位移
displacements = np.linalg.solve(K, F)

# 7. 计算应力
stresses = np.zeros(num_elements)
for i in range(num_elements):
    stresses[i] = (E / element_length) * (displacements[i+1] - displacements[i])

# 8. 使用 VTK 可视化结果
# 创建点
points = vtkPoints()
for x in node_coords:
    points.InsertNextPoint(x, 0, 0)

# 创建单元
cells = vtkCellArray()
for i in range(num_elements):
    triangle = vtkTriangle()
    triangle.GetPointIds().SetId(0, i)
    triangle.GetPointIds().SetId(1, i+1)
    cells.InsertNextCell(triangle)

# 创建网格
grid = vtkUnstructuredGrid()
grid.SetPoints(points)
grid.SetCells(5, cells)  # 5 表示单元类型为三角形

# 添加位移数据
displacement_array = vtkFloatArray()
displacement_array.SetName("Displacement")
for d in displacements:
    displacement_array.InsertNextValue(d)
grid.GetPointData().AddArray(displacement_array)

# 添加应力数据
stress_array = vtkFloatArray()
stress_array.SetName("Stress")
for s in stresses:
    stress_array.InsertNextValue(s)
grid.GetCellData().AddArray(stress_array)

# 显示变形
warp = vtkWarpVector()
warp.SetInputData(grid)
warp.SetScaleFactor(1.0)

mapper = vtkDataSetMapper()
mapper.SetInputConnection(warp.GetOutputPort())

actor = vtkActor()
actor.SetMapper(mapper)

renderer = vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)

render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)

interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

render_window.Render()
interactor.Start()