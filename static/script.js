// script.js

// 示例：发送数据到后端
async function sendData() {
    const data = {
      seldrop: "示例选择",
      output: "示例输出",
      vtkpane: "示例VTK Pane"
    };
  
    try {
      const response = await fetch('/api/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
  
      const result = await response.json();
      console.log("后端返回的数据：", result);
      alert("后端返回的数据：" + JSON.stringify(result));
    } catch (error) {
      console.error("发送数据时出错：", error);
    }
  }