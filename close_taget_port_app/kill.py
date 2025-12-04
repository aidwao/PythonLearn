import sys
import subprocess
from typing import List

def get_func_name(stack_depth = 1):
	"""
	获得当前函数名
	stack_depth: 堆栈深度
	"""
	try:
		return sys._getframe(stack_depth).f_code.co_name
	except Exception as e:
		print('UIDebug: get_func_name: err msg: %s' % (str(e)))
		return ''

def _needs_shell(cmd: List[str]) -> bool:
	"""
	判断命令是否需要 shell
	
	需要 shell 的情况：
	1. 命令是字符串且包含管道 |
	2. 命令包含重定向 >, <, >>
	3. 命令包含 && 或 ||
	4. 命令包含通配符 * ?
	"""
	# 字符串形式：检查是否包含 shell 特殊字符
	shell_chars = ['|', '>', '<', '&&', '||', ';', '&']
	for str in cmd:
		if any(char in str for char in shell_chars):
			return True
	return False

def _safe_decode(data: bytes) -> str:
    """安全解码（尝试多种编码）"""
    if not data:
        return ""
    
    # 尝试顺序：gbk → utf-8 → latin1
    encodings = ['gbk', 'utf-8', 'latin1']
    
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue
    
    # 最后兜底：替换错误字符
    return data.decode('gbk', errors='replace')


def run_win_command(command : list):
	"""执行windows命令，返回输出"""
	try:
		# 不弹黑窗口
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		need_shell = _needs_shell(command)
		print(f"start run_win_command: {need_shell=}")
		result = subprocess.run(command, 
						  	capture_output=True, 
						  	text=False, 
						  	check=True,
							# encoding='utf-8',
							startupinfo=startupinfo,
							shell=True
						  )
		output = _safe_decode(result.stdout)
		return output
	except subprocess.CalledProcessError as e:
		print(f"func:{get_func_name(2)} run_win_command CalledProcessError: {e}")
	except Exception as e:
		print(f"func:{get_func_name(2)} run_win_command error: {e}")
	return ''

def extract_pids(netstat_output: str) -> int:
	"""从 netstat 输出中提取所有 PID"""
	if not netstat_output:
		return 0
	count_dict : dict[int, int]= {}
	for line in netstat_output.strip().split('\n'):
		parts = line.split()
		if parts and parts[-1].isdigit():
			pid = int(parts[-1])
			if pid != 0:
				count_dict[pid] = count_dict.get(pid, 0) + 1
	
	# 去重并排序
	max_key = 0
	if count_dict:
		max_key = max(count_dict, key=count_dict.get)
	return max_key

def get_max_num_pid(port : int):
	command = ["netstat", "-ano", "|", "findstr", f":{port}"]
	output = run_win_command(command)
	max_pid = extract_pids(output)
	print(f"get_max_num_pid max_pid: {max_pid}")
	return max_pid

def kill_taget_port(port : int):
	"""杀死指定端口的进程"""
	while(pid := get_max_num_pid(port)):
		command = ["taskkill", "/F", "/PID", str(pid)]
		print(f"kill pid: {pid}")
		run_win_command(command)
		
	print("kill_taget_port done")

kill_taget_port(5678)