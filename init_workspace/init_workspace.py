import argparse, sys, re, json, os
import subprocess

def to_win_cmd_path(path):
	"""将路径转换为Windows命令行格式"""
	path = normalize_path(path)
	return os.path.normpath(path).replace('/', '//')

def normalize_path(path):
	import os
	return os.path.normpath(path).replace('\\', '/')

def open_win_folder(folder_path):
	folder_path = to_win_cmd_path(folder_path)
	command = f'explorer "{folder_path}"'
	exit_code = os.system(command)
	if exit_code == 1:
		print(f"成功打开文件夹: {folder_path}")
	else:
		print(f"打开文件夹失败，错误代码: {exit_code}")

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

def run_win_command(command : list):
	"""执行windows命令，返回输出"""
	try:
		# 不弹黑窗口
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		result = subprocess.run(command, 
						  	capture_output=True, 
						  	text=True, 
						  	check=True,
							encoding='utf-8',
							startupinfo=startupinfo,
						  )
		output = result.stdout
		return output
	except subprocess.CalledProcessError as e:
		print(f"func:{get_func_name(2)} run_win_command CalledProcessError: {e}")
	except Exception as e:
		print(f"func:{get_func_name(2)} run_win_command error: {e}")
	return []

def create_p4_config(workspace_name : str, user_name : str, full_path : str):
	try:
		with open(f"{full_path}/.p4config", "w") as f:
			f.write(
		f'''P4PORT=ssl:x20.perforce.nie.netease.com:1666
P4USER={user_name}
P4CLIENT={workspace_name}''')
		print(f'.p4config文件创建完成: {workspace_name}')
	except IOError as e:
		print(f"创建.p4config文件时出错: {e}")



# 常量定义
WORKSPACE_TEMPLATE = {
	"folders": [
		{"path": "./Content/Marvel/Scripts"},
		{"path": "./Config"},
		{"path": "./Content/Marvel/EditorOnly/Scripts"},
		{"path": "./doc"},
		{"path": "./Content/Localization/Game"},
		{"path": "./Source"},
		{"path": "./Plugins"}
	],
	"settings": {
		"python.autoComplete.extraPaths": [],
		"python.analysis.extraPaths": [],
		"perforce.port": "ssl:x20.perforce.nie.netease.com:1666",
		"perforce.debugModeActive": True,
		"perforce.deleteOnFileDelete": True,
		"perforce.editOnFileModified": True,
		"perforce.editOnFileSave": True,
		"perforce.addOnFileCreate": True,
		"files.associations": {
			"regex": "cpp",
			"sstream": "cpp",
			"*.rh": "cpp"
		}
	}
}

def create_workspace_file(workspace_name, user_name, branch_name, full_path):
	workspace_template = WORKSPACE_TEMPLATE.copy()
	absolute_path = os.path.join(full_path, 'UnrealEngine', 'Marvel')
	# 更新配置
	workspace_template["settings"]["perforce.user"] = user_name
	workspace_template["settings"]["perforce.client"] = workspace_name

	extra_paths = []
	for extra_path in WORKSPACE_TEMPLATE['folders']:
		extra_path = extra_path['path']
		extra_path = extra_path.replace('./', '')
		extra_path = extra_path.replace('/', '\\')
		extra_paths.append(absolute_path + '\\' +extra_path)

	for path in extra_paths:
		full_path = os.path.join(absolute_path, path)
		workspace_template["settings"]["python.autoComplete.extraPaths"].append(full_path)
		workspace_template["settings"]["python.analysis.extraPaths"].append(full_path)

	# 创建文件
	file_name = f"Marvel_{branch_name}.code-workspace"
	file_path = os.path.join(absolute_path, file_name)

	try:
		with open(file_path, "w") as f:
			workspace_template = json.dumps(workspace_template, ensure_ascii=False,indent=4)
			f.write(workspace_template)
		print(f'code-workspace文件创建完成: {file_path}')
		open_win_folder(absolute_path)
	except IOError as e:
		print(f"创建code-workspace文件时出错: {e}")

def main_function(workspace_name):
	workspace_info_str = run_win_command(["p4", "client", "-o", f"{workspace_name}"])
	lines = workspace_info_str.split('\n')
	root_path = ''
	user_name = ''
	stream_name = ''
	for line in lines:
		if line.startswith('Root:'):
			root_path = line.split(':', 1)[1].strip()
		elif line.startswith('Owner:'):
			user_name = line.split(':', 1)[1].strip()
		elif line.startswith('Stream:'):
			stream_name = line.split('/')[-1].strip()
	
	print(f" p4 workspace info : {root_path=} {user_name=} {stream_name=}")
	if not root_path or not user_name or not stream_name:
		return False
	
	create_p4_config(workspace_name, user_name, root_path)

	create_workspace_file(workspace_name, user_name, stream_name, root_path)

	return True

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("workspace", type=str)
	args = parser.parse_args()
	workspace_name = args.workspace
	print(f" start init workspace {workspace_name=} ")
	success = main_function(workspace_name)
	print(f" end init {success=} ")

		
