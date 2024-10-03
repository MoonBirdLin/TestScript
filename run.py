import os
import argparse
import pathlib
import sys
import signal
import subprocess
import traceback

def mkdir(path): 
	if not os.path.exists(path):
		os.makedirs(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start App Exploration')
    parser.add_argument('package', metavar='P', type=str, nargs=1,
                    help='package name')
    
    app = parser.parse_args().package[0]


    current_dir = os.getcwd()
    APKS_DIR = os.path.join(current_dir,"apks")
    Output_DIR = os.path.join(current_dir,"res",app)
    mkdir(Output_DIR)

    Network_script = os.path.join(current_dir,"network","networkflow.py")
    Network_script_new = os.path.join(Output_DIR,"networkflow_"+app+".py")
    Network_output = os.path.join(Output_DIR,"network.json")
    Network_Log = os.path.join(Output_DIR,"network_log.txt")
    pathlib.Path(Network_output).touch()

    sed_cmd = ["sed","18s/+++++/"+Network_output.replace("\\", "\\\\\\\\")+"/",Network_script]
    # 我的主机莫名其妙8080端口无法抓包, 就改成了12789
    mitmdump_cmd = ["mitmdump","-p", "12789", "-s", Network_script_new]

    Hook_output = os.path.join(Output_DIR,"hook.xls")
    Hook_cmd = "python ./hook/camille.py " + app + " -es ./hook/script_encrypt.js -npp -f " + Hook_output
    Hook_Log = os.path.join(Output_DIR,"hook_log.txt")
    pathlib.Path(Hook_output).touch()
	
    try:
        subprocess.run(["adb","install",os.path.join(APKS_DIR,app+".apk")])
        subprocess.run(["adb","shell","am kill-all"])
        print("App installed")

        fd1 = os.open(Network_script_new, os.O_RDWR | os.O_CREAT)
        fd2 = os.open(Network_Log, os.O_RDWR | os.O_CREAT)
        fd3 = os.open(Hook_Log, os.O_RDWR | os.O_CREAT)
        subprocess.run(sed_cmd, stdout=fd1)
        os.close(fd1)
        print("generate mitm script")
        proc1 = subprocess.Popen(mitmdump_cmd, stdout=fd2)
        print("mitm started")
        
        proc2 = subprocess.Popen(Hook_cmd.split(), stdout=fd3)
        print("Hook started")

        print(f"proc1.pid: {proc1.pid}")
        print(f"proc2.pid: {proc2.pid}")
        
        message = input("终止时请输入任意字符：")
        if message:
            # proc2.kill()
            # proc2.send_signal(signal.CTRL_C_EVENT)
            # proc2.communicate()
            proc1.terminate()
            proc1.communicate()
            os.close(fd2)
            print("mitm terminated")
            # windows 有 bug, 直接用terminate, camile 进程莫名其妙无法正常执行 SIGTERM 和 SIGINT 的 Handler 进程, 就直接被 kill 掉
            # 经过测试一个有效解决方案是再父进程(当前进程)中打一个 CTRL-C 信号, SIGINT就会被传递到子进程中, 就能正常记录log
            # 因此此处的解决方案是先把 mitmdump 的进程用 terminate kill掉, 然后提示用户用 ctrl-c 杀掉进程; 然后为了正常等待用户使用 ctrl-c kill 掉进程, 这里先communicate一下, 然后再Exception处理中用os.close关闭句柄
            print("please type ctrl-c to kill camille!")
            proc2.communicate()
            os.close(fd3)
            # subprocess.run(["taskkill.exe", "/t", "/f", "/pid", str(proc2.pid)])
            # subprocess.run([".\\windows-kill_x64\\windows-kill.exe", "-SIGINT", str(proc2.pid)])
            # subprocess.run([".\\windows-kill_Win32\\windows-kill.exe", "-SIGINT", str(proc2.pid)])
    except KeyboardInterrupt as e:
        print("KeyboardInterrupt Got")
        proc2.communicate()
        # os.close(fd2)
        os.close(fd3)
    except Exception as e:
        print(e) 
        
	