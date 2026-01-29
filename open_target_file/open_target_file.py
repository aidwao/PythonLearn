import os
import argparse

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
	parser = argparse.ArgumentParser(description='Open a file')
	parser.add_argument('args', type=str, nargs='*', help='all args')
	args = parser.parse_args()
	print(f"args: {args}")
	final_args = args.args
	print(f"final_args: {final_args}")
	path = r"G:\workspace\test_ugs_sync\UnrealEngine\UE5.sln"
	folder_path_list = path.split('\\')[:-1]
	folder_path = '\\'.join(folder_path_list)
	if len(final_args) > 0:
		if ("f" in final_args):
			open_file(folder_path)
	else:
		open_file(r"G:\workspace\test_ugs_sync\UnrealEngine\UE5.sln")
