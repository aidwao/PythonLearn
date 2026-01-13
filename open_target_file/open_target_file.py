import os

def normalize_path(path):
	import os
	return os.path.normpath(path).replace('\\', '/')

def to_win_cmd_path(path):
	"""将路径转换为Windows命令行格式"""
	path = normalize_path(path)
	import os
	return os.path.normpath(path).replace('/', '//')

def open_file(file_path):
	file_path = to_win_cmd_path(file_path)
	exit_code = os.startfile(file_path)
	print(f"打开文件: {file_path} {exit_code=}")

if __name__ == "__main__":
	open_file(r"G:\workspace\test_ugs_sync\UnrealEngine\UE5.sln")
