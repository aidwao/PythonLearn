import re, os, sys
import subprocess
import argparse

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

def py_depot_path_to_relative_path(depot_path:str):
	file_path = normalize_path(depot_path)
	parts = file_path.split('/')
	try:
		index = parts.index('Scripts')
		return '/'.join(parts[index:])
	except ValueError:
		print(f"Could not find UnrealEngine in path: {depot_path}")
		return ''

def get_changelist_files(changelist_num):
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
			files = []
			# 分割成行并去除每行开头的空白字符
			for line in affected_files.split('\n'):
				line = line.strip()
				if line and not line.startswith('... #'):
					action_and_file = line.split()
					if len(action_and_file) >= 3:
						action, file_path = action_and_file[2], action_and_file[1]
						if action.lower() != 'delete':
							files.append(file_path)
			return files
		else:
			return []

	command = [
		"p4",
		"describe",
		"-S",
		str(changelist_num)
	]
	output = run_win_command(command)
	if output:
		return extract_affected_files(output)
	return []

def fetch_and_save_file_from_perforce(perforce_path, destination_path, changelist_num):
	# 步骤1: 解析Perforce路径和版本号
	depot_path, version = parse_perforce_path(perforce_path)
	
	# 步骤2: 确保目标文件夹存在,如果不存在则创建
	os.makedirs(os.path.dirname(destination_path), exist_ok=True)
	
	# 步骤3: 使用p4 print命令获取指定版本的文件内容
	output = run_win_command(['p4', 'print', f'{depot_path}@={changelist_num}'])
	
	# 步骤4: 去掉第一行（//depot 路径信息），只保留文件内容
	file_content = '\n'.join(output.split('\n')[1:])

	# 步骤5: 将内容写入目标文件
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
	if exit_code == 0:
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

def _create_scripts_folder_from_changelist(changelist_num = 0):
	"""尝试创建Windows文件夹"""
	if isinstance(changelist_num, str):
		if changelist_num.isdigit():
			changelist_num = int(changelist_num)
		else:
			print(f'CreateScriptsFolder: change num invalid {changelist_num=}')
			return

	files = get_changelist_files(changelist_num)
	unreal_parent_path = get_full_path() + "/OverlayFolder"
	toolbox_parent_path = "Windows/Marvel/Content/Marvel"
	# 删除OverlayFolder文件夹
	win_remove_file_or_folder(f"{unreal_parent_path}")

	files_str = ''
	if files:
		for file in files:
			depot_path, version = parse_perforce_path(file)
			if not depot_path.endswith('.py'):
				continue
			files_str += f'{file} \n'
			new_path = py_depot_path_to_relative_path(depot_path)
			
			target_path = f"{unreal_parent_path}/{toolbox_parent_path}/{new_path}"
			fetch_and_save_file_from_perforce(file, target_path, changelist_num)

		if files_str:
			# 压缩文件夹(有文件被复制才压缩)
			zip_folder_to_owning_folder(f"{unreal_parent_path}/Windows")

			# 成功之后，打开文件夹
			open_win_folder(unreal_parent_path)
		
	print(f'CreateScriptsFolder: task complete {changelist_num=} \n {files_str}')

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("changelist", type=int, help="Changelist number")
	args = parser.parse_args()
	changelist_num = args.changelist
	print(f'CreateScriptsFolder: task start {changelist_num=}')
	if isinstance(changelist_num, str):
		if changelist_num.isdigit():
			changelist_num = int(changelist_num)
		else:
			print(f'CreateScriptsFolder: change num invalid {changelist_num=}')

	_create_scripts_folder_from_changelist(changelist_num)