# VTK-PANEL-FASTAPI
---

## 快速上手/quick start

在本目录下
```
bash
> pip install -r requirements.txt
Then
> uvicorn main:app --reload
Or
> ./start.bat
```
如果是梁加载
```
> uvicorn beam:app  --reload
```

---
## branch
- master 主分支
- develop 开发分支
- learn 学习分支
- dev-panel 纯panel前端分支
> 我意识到html+panel可能有点蠢



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
    > 纯panel实现 在分支dev-panel里
    - [x] 实现一个简单3d模型展示
    - [ ] 实现一个可以自己·输入简支梁参数,包括
        - 长度L
        - 高度H
        - 弹性模量E
        - 均布荷载q
        - 单元数量N
- [ ] 一个展示各种函数的教程页面
    > panel杂交html实现 在分支develop里

---

## Issue
- [x] 在静态html中替换panel生成的html会导致panel的回调和响应函数无作用
> 利用奇妙的不懂原理的嵌入了html然后就可以了？
- [x] 并发访问生成vtk对象会导致资源占用爆错
> 多次调用 并发调用时 单独编写单例模式来统一规定vtk对象的渲染行为
- [x] 重置摄像机实则也需要重置actor对象 不然位置不对
> 这条的理解是错误的 实际上重置不完全是由于摄像机并不只有三个位置参数导致的
> 另外生成新对象之后不同视角实际上是生成参数传递错了
- [ ] 切换template子元素的时候并不自动更新（甚至手动更新也不行！）
- [x] notifications的持续时间并不按照赋值，不清楚其中有没有错误的内部实现和不明晰的机制
> 系组件库自身原因 会在第一个注销后连同注销的机制导致的
- [ ] vtkmanager的缓存功能存在严重缺陷 应该添加一个hash方法
- [x] 并不能真正做到用到fastapi！
> 算是做到了吧.
- [x] 调用vtkrenderinteracter的start方法后deadlock
> 由于并非单独vtk运用 此方法会进入vtk的事件循环直到调用terminateApp() 在web场景中不适用 转而寻求panel的解决方法
