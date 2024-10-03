# 人工测试工具

## 测试设备要求
1. 设备已安装mitmproxy证书为系统证书，并配置好wifi转发端口
2. 设备已安装frida-server==16.3.3，或者Magisk安装[林博的MagiskFlorida模块](https://github.com/MoonBirdLin/magisk-frida/releases)

## 运行环境要求
1. 安装所需包
   `pip install -r requirements.txt`

## 使用步骤
1. 在`apks/`文件夹中存放需测试应用安装包
2. 连接测试设备，启动frida-server，建议进行以下几条测试：
   1. `frida-ps -U`指令是否可正确输出结果
   2. `adb shell netstat -atp | grep 27042`是否已启动frida-server
3. `python3 run.py {package id}`
4. 手动操作应用完成点击、输入等行为
5. 操作结束后输入任意字符回车后等待程序停止。

## 输出
1. Log: `res/{package id}/hook_log.txt`, `res/{package id}/network_log.txt`
2. Result: `res/{package id}/hook.xls`, `res/{package id}/network.json`

