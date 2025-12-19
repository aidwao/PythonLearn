import re, os, sys
import subprocess
import argparse
from pathlib import Path

def normalize_path(path):
	import os
	return os.path.normpath(path).replace('\\', '/')

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

def to_win_cmd_path(path):
	"""将路径转换为Windows命令行格式"""
	path = normalize_path(path)
	import os
	return os.path.normpath(path).replace('/', '//')

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

def get_current_branch_name():
	# 运行 p4 info 命令
	command = ["p4", "info"]
	output = run_win_command(command)

	# 解析输出以获取 Client stream
	client_stream_match = re.search(r"Client stream: (.+)", output)
	if not client_stream_match:
		print("Could not find Client stream in p4 info output")
		return ''

	client_stream = client_stream_match.group(1)

	return client_stream

def parse_perforce_path(perforce_path:str):
	splited = perforce_path.split('#')
	if len(splited) != 2:
		print(f"Could not parse depot path: {perforce_path}")
		return '' , 0

	depot_path = splited[0]
	version = int(splited[1])
	return depot_path, version

def get_full_path():
	# 获取当前脚本的绝对路径
	import os
	if getattr(sys, 'frozen', False):
		# 如果是打包后的 .exe
		application_path = sys.executable
	else:
		# 如果是普通 Python 脚本
		application_path = os.path.abspath(__file__)
	parent_directory = os.path.dirname(application_path)
	return normalize_path(parent_directory)

def py_depot_path_to_relative_path(depot_path:str, need_file_name=True):
	file_path = normalize_path(depot_path)
	parts = file_path.split('/')
	try:
		index = parts.index('Scripts')
		if need_file_name:
			path = '/'.join(parts[index:])
		else:
			path = '/'.join(parts[index:-1])
		return path
	except ValueError:
		print(f"Could not find UnrealEngine in path: {depot_path}")
		return ''

def filter_depot_file_paths(depot_files):
	if depot_files:
		files = []
		# 分割成行并去除每行开头的空白字符
		for line in depot_files.split('\n'):
			line = line.strip()
			if line and not line.startswith('... #'):
				action_and_file = line.split()
				if len(action_and_file) >= 3:
					file_path:str
					action, file_path = action_and_file[2], action_and_file[0]
					if action.lower() != 'delete':
						real_file_path = file_path.split('#')[0]
						if real_file_path.endswith('.py'):
							files.append(real_file_path)
		return files
	else:
		return []

def get_single_changelist_local_changelist_files(workspace_name, changelist_num) -> list[tuple]:
	""" 获取本地文件列表 """
	command = [
		"p4",
		"-c",
		workspace_name,
		"opened",
		"-c",
		str(changelist_num)
	]
	output = run_win_command(command)
	filted_depot_files = filter_depot_file_paths(output)
	result_files = []
	for file_path in filted_depot_files:
		command = [
			"p4",
			"-c",
			workspace_name,
			"where",
			file_path
		]
		output = run_win_command(command)
		print(f" {output=}")
		if not output:
			continue
		real_path = output.split()[2]
		result_files.append((file_path, real_path))
	return result_files

def get_local_changelist_files(workspace_name, changelist_num_list) -> list[tuple]:
	""" 获取本地文件列表 """
	result_files = []
	for changelist_num in changelist_num_list:
		files = get_single_changelist_local_changelist_files(workspace_name, changelist_num)
		result_files.extend(files)
	return list(set(result_files))

def get_server_changelist_file_dict(changelist_num_list):
	def extract_affected_files(text):
		# 使用正则表达式匹配 "Affected files ..." 和下一个空行之间的内容
		pattern = r"Affected files \.\.\.(.+?)(?:\n\s*\n|\Z)"
		match = re.search(pattern, text, re.DOTALL)
		if not match:
			# 如果没找到提交影响文件，下降查找shelve file
			pattern = r"Shelved files \.\.\.(.+?)(?:\n\s*\n|\Z)"
			match = re.search(pattern, text, re.DOTALL)
		if match:
			affected_files = match.group(1).strip()
			if affected_files:
				# 分割成行并去除每行开头的空白字符
				file_dict = {}
				for line in affected_files.split('\n'):
					line = line.strip()
					if line and not line.startswith('... #'):
						action_and_file = line.split()
						if len(action_and_file) >= 3:
							action, file_path = action_and_file[2], action_and_file[1]
							if action.lower() != 'delete':
								real_file_path = file_path.split('#')[0]
								if real_file_path.endswith('.py'):
									file_dict[real_file_path] = changelist_num
				return file_dict
			else:
				return {}
		else:
			return {}
		
	sorted_changelists = sorted(list(set(changelist_num_list)))
	print(f"{sorted_changelists=}")
	result_files = {}
	for changelist_num in sorted_changelists:
		command = [
			"p4",
			"describe",
			"-S",
			str(changelist_num)
		]
		output = run_win_command(command)
		if not output:
			continue
		finded_files = extract_affected_files(output)
		if finded_files:
			result_files.update(finded_files)
	return result_files

def fetch_and_save_file_from_perforce(depot_path, destination_path, changelist_num):
	# 步骤1: 确保目标文件夹存在,如果不存在则创建
	os.makedirs(os.path.dirname(destination_path), exist_ok=True)
	
	# 步骤2: 使用p4 print命令获取指定版本的文件内容
	output = run_win_command(['p4', 'print', f'{depot_path}@={changelist_num}'])
	
	# 步骤3: 去掉第一行（//depot 路径信息），只保留文件内容
	file_content = '\n'.join(output.split('\n')[1:])

	# 步骤4: 将内容写入目标文件
	with open(destination_path, 'w', encoding='utf-8') as f:
		try:
			f.write(file_content)
		finally:
			f.close()
	
	print(f"文件已成功保存到: {destination_path}")

def open_win_folder(folder_path):
	import os
	folder_path = to_win_cmd_path(folder_path)
	command = f'explorer "{folder_path}"'
	exit_code = os.system(command)
	if exit_code == 1:
		print(f"成功打开文件夹: {folder_path}")
	else:
		print(f"打开文件夹失败，错误代码: {exit_code}")

def win_remove_file_or_folder(path:str):
	"""删除文件或文件夹"""
	# 检查路径是否存在
	import os, subprocess
	path = to_win_cmd_path(path)
	if not os.path.exists(path):
		print(f"路径不存在 不需要删除: {path}")
		print()
		return

	try:
		# 检查是否为目录
		if os.path.isdir(path):
			command = f'rmdir /s /q "{path}"'
			exit_code = os.system(command)
			if exit_code == 0:
				print(f"成功删除目录: {path}")
			else:
				print(f"删除目录失败，错误代码: {exit_code}")
		elif os.path.isfile(path):
			command = f'del /f /q "{path}"'
			exit_code = os.system(command)
			if exit_code == 0:
				print(f"成功删除文件: {path}")
			else:
				print(f"删除文件失败，错误代码: {exit_code}")
		else:
			print(f"路径不存在或不是文件或目录: {path}")
	except (OSError, subprocess.CalledProcessError) as e:
		print(f"删除失败 {path} \n 错误: {str(e)}")
	print()


def zip_folder_to_owning_folder(folder_path):
	"""压缩文件夹到同级目录"""
	import os
	folder_path = normalize_path(folder_path)
	parent_path = os.path.dirname(folder_path)
	path_name = os.path.basename(folder_path)
	command = f'cd /d {parent_path} && tar -cavf {path_name}.zip {path_name}'
	exit_code = os.system(command)
	if exit_code == 0:
		print(f"成功压缩文件夹: {path_name}")
	else:
		print(f"压缩文件夹失败，错误代码: {exit_code}")

def move_local_file_to_target_file_path(local_path, target_path):
	os.makedirs(target_path, exist_ok=True)
	command = f'copy {local_path} {target_path}'
	run_output = os.system(command)
	if run_output == 0:
		print(f"移动文件 {local_path} 成功")
	else:
		print(f"移动文件 {local_path} to {target_path} 失败")

def _create_scripts_folder_from_changelist(workspace_name, changelist_num_list):
	"""尝试创建Windows文件夹"""
	file_dict = get_server_changelist_file_dict(changelist_num_list)
	if workspace_name:
		local_files = get_local_changelist_files(workspace_name, changelist_num_list)
	else:
		local_files = []

	unreal_parent_path = get_full_path() + "/OverlayFolder"
	toolbox_parent_path = "Windows/Marvel/Content/Marvel"
	# 删除OverlayFolder文件夹
	win_remove_file_or_folder(f"{unreal_parent_path}")
	files_str = ''
	if local_files:
		files_str += '以下文件被复制:\n'
		print("开始处理本地文件：")
		for file in local_files:
			depot_file_path, local_file_path = file
			if depot_file_path in file_dict:
				print(f'file exist local {depot_file_path=}, prefer use local file')
				file_dict.pop(depot_file_path)
			new_path = py_depot_path_to_relative_path(depot_file_path, False)
			target_path = f"{unreal_parent_path}/{toolbox_parent_path}/{new_path}"
			target_path = to_win_cmd_path(target_path)
			move_local_file_to_target_file_path(local_file_path, target_path)
			files_str += f'{local_file_path} \n'
	
	print()
	print("开始处理下载文件：")
	if file_dict:
		files_str += '以下文件被下载:\n'
		for depot_path, changelist_num in file_dict.items():
			if not depot_path.endswith('.py'):
				continue
			files_str += f'{depot_path} {changelist_num} \n'
			new_path = py_depot_path_to_relative_path(depot_path)
			
			target_path = f"{unreal_parent_path}/{toolbox_parent_path}/{new_path}"
			fetch_and_save_file_from_perforce(depot_path, target_path, changelist_num)

	print()
	if files_str:
		# 压缩文件夹(有文件被复制才压缩)
		zip_folder_to_owning_folder(f"{unreal_parent_path}/Windows")

		# 成功之后，打开文件夹
		open_win_folder(unreal_parent_path)
	else:
		print(f'目标changelist{changelist_num_list=}没有py文件')
	print()
	print(f'CreateScriptsFolder: task complete {changelist_num_list=} \n {files_str}')

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	# parser.add_argument("workspace", type=str, help="Workspace Name")
	parser.add_argument("all_args", type=str, nargs='*', help="ALL Arguments")
	args = parser.parse_args()
	all_args = args.all_args
	print(f'CreateScriptsFolder: task start {all_args=}')
	if len(all_args) > 0:
		workspace_name = all_args[0]
		check_output = run_win_command(['p4', 'clients', '-e', workspace_name])
		print(f"{check_output=}")
		if check_output:
			changelist_num_list = all_args[1:]
			print(f'CreateScriptsFolder: task start {workspace_name=} {changelist_num_list=}')
			print()

			_create_scripts_folder_from_changelist(workspace_name, changelist_num_list)
		else:
			changelist_num_list = all_args
			_create_scripts_folder_from_changelist('', changelist_num_list)
	else:
		print("Usage: python CreateScriptsFolder.py <workspace> <changelist_num1> <changelist_num2> or python CreateScriptsFolder.py <changelist_num1> <changelist_num2> ...")