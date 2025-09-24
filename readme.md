# VTK-PANEL-FASTAPI
---

## 快速上手/quick start

在本目录下
```
bash
> pip install -r requirements.txt
> uvciorn main:app 
Or
> ./start.bat
```

---
## branch
- master 主分支
- develop 开发分支
- learn 学习分支




---
## To Do

- [x] 初步认识vtk，panel，fastapi
> vtk图形化，panel前端，在数据显示比较方便，fastapi快速简单的创建在线内容
- [x] 一个简单的vtk立方体嵌在panel里通过fastapi路由转发
> pn.extension('vtk') 
- [x] 搞清楚vtk和panel的交互模式
- [x] 做到更好的样式编辑 提前写好css+html然后嵌入panel
> 在已经定义好的静态或者加js，css的html文件里提前打好标识，然后runtime替换
- [ ] 实现一个在线生成各种3d模型并编辑的网站
- [ ] 一个展示各种函数的教程页面

---

## Issue
- [ ] pylance无法检查动态语法！
- [ ] 在静态html中替换panel生成的html会导致panel的回调和响应函数无作用
- [ ] 并发访问生成vtk对象会导致资源占用爆错
- [ ] pylance无法检查动态生成的属性，会有偏差