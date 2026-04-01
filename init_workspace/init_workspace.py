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
		{
			"name": "UE5",
			"path": "."
		},
		{
			"name": "Scripts",
			"path": "./Marvel/Content/Marvel/Scripts"
		},
		{
			"name": "EditorScripts",
			"path": "./Marvel/Content/Marvel/EditorOnly/Scripts"
		},
		{
			"name": "Config",
			"path": "./Marvel/Config"
		},
		{
			"name": "Docs",
			"path": "./Marvel/doc"
		},
		{
			"name": "Localization",
			"path": "./Marvel/Content/Localization/Game"
		},
		{
			"name": "Source",
			"path": "./Marvel/Source"
		},
		{
			"name": "Plugins",
			"path": "./Marvel/Plugins"
		}
	],
	"settings": {
		"npm.autoDetect": "off",
		"[python]": {
			"editor.defaultFormatter": "ms-python.autopep8",
			"editor.insertSpaces": False,
			"editor.tabSize": 4
		},
		"python.languageServer": "Pylance",
		"python.analysis.autoSearchPaths": False,
		"python.analysis.userFileIndexingLimit": 5000,
		"python.analysis.typeCheckingMode": "off",
		"python.analysis.exclude": [
			"${workspaceFolder:UE5}/**",
			"${workspaceFolder:Config}/**"
		],
		"python.analysis.stubPath": "${workspaceFolder:Docs}",
		"python.autoComplete.extraPaths": [
			"${workspaceFolder:Scripts}",
			"${workspaceFolder:Scripts}/../EditorOnly/Scripts",
			"${workspaceFolder:Scripts}/../ScriptLibs/Python311/site-packages",
			"${workspaceFolder:Scripts}/../ScriptLibs/Python311/site-packages-dev",
			"${workspaceFolder:Config}",
			"${workspaceFolder:Docs}",
			"${workspaceFolder:Localization}",
			"${workspaceFolder:Source}",
			"${workspaceFolder:Plugins}"
		],
		"python.analysis.extraPaths": [
			"${workspaceFolder:Scripts}",
			"${workspaceFolder:Scripts}/../EditorOnly/Scripts",
			"${workspaceFolder:Scripts}/../ScriptLibs/Python311/site-packages",
			"${workspaceFolder:Scripts}/../ScriptLibs/Python311/site-packages-dev",
			"${workspaceFolder:Config}",
			"${workspaceFolder:Docs}",
			"${workspaceFolder:Localization}",
			"${workspaceFolder:Source}",
			"${workspaceFolder:Plugins}"
		],
		"flake8.args": [
			"--config=${workspaceFolder:Docs}/.conf/flake8.ini"
		],
		"python.formatting.provider": "yapf",
		"python.formatting.yapfArgs": [
			"--style=${workspaceFolder:UE5}/.config/.style.yapf"
		],
		"autopep8.args": [
			"--global-config=${workspaceFolder:UE5}/.config/.pycodestyle"
		],
		"black-formatter.args": [
			"--config=${workspaceFolder:UE5}/.config/.style.black"
		],
		"pylint.cwd": "${workspaceFolder:UE5}",
		"pylint.args": [
			"--rcfile=${workspaceFolder:UE5}/.config/.pylintrc"
		],
		"perforce.port": "ssl:x20.perforce.nie.netease.com:1666",
		"perforce.debugModeActive": True,
		"perforce.deleteOnFileDelete": True,
		"perforce.editOnFileModified": True,
		"perforce.editOnFileSave": True,
		"perforce.addOnFileCreate": True,
		"perforce.user": "",
		"perforce.client": "",
		"files.associations": {
			"regex": "cpp",
			"sstream": "cpp",
			"*.rh": "cpp"
		},
		"files.exclude": {
			".vs/**": True,
			"FeaturePacks/**": True,
			"Gaming.Xbox.Scarlett.x64/**": True,
			"Minima/**": True,
			"Samples/**": True,
			"ORBIS_Development/**": True,
			"Templates/**": True
		},
		"search.exclude": {
			"Engine/**": True,
			"openspec/**": True,
			"undefined/**": True,
			"InterchangeWorker/**": True,

			"Marvel/Binaries/**": True,
			"Marvel/Build/**": True,
			"Marvel/DerivedDataCache/**": True,
			"Marvel/Intermediate/**": True,
			"Marvel/Internationalization/**": True,
			"Marvel/LocalCheckScripts/**": True,
			"Marvel/Marvel/**": True,
			"Marvel/PackageCheckRecords/**": True,
			"Marvel/Platforms/**": True,
			"Marvel/Projects/**": True,
			"Marvel/Saved/**": True,
			"Marvel/Tools/**": True,
			"Marvel/autobuild/**": True,

			"Marvel/Content/Collections/**": True,
			"Marvel/Content/DebutTrailer/**": True,
			"Marvel/Content/Developers/**": True,
			"Marvel/Content/Global/**": True,
			"Marvel/Content/L10N/**": True,
			"Marvel/Content/MarvelDemo/**": True,
			"Marvel/Content/Marvel_LQ/**": True,
			"Marvel/Content/Marvel_NeverCook/**": True,
			"Marvel/Content/MoviesBink/**": True,
			"Marvel/Content/Oodle/**": True,
			"Marvel/Content/PakRecord/**": True,
			"Marvel/Content/Splash/**": True,
			"Marvel/Content/Temp/**": True,

			"Marvel/Content/Localization/Encrypt/**": True,

			"Marvel/Content/Marvel/AI/**": True,
			"Marvel/Content/Marvel/AbilitySystem/**": True,
			"Marvel/Content/Marvel/AntiCheat/**": True,
			"Marvel/Content/Marvel/AssetAuditor/**": True,
			"Marvel/Content/Marvel/Audio/**": True,
			"Marvel/Content/Marvel/Blueprints/**": True,
			"Marvel/Content/Marvel/Chaos/**": True,
			"Marvel/Content/Marvel/Characters/**": True,
			"Marvel/Content/Marvel/Cutscenes/**": True,
			"Marvel/Content/Marvel/Data/**": True,
			"Marvel/Content/Marvel/DataTable/**": True,
			"Marvel/Content/Marvel/EditorOnly/AutoExportText/**": True,
			"Marvel/Content/Marvel/EditorOnly/BlueprintUtilities/**": True,
			"Marvel/Content/Marvel/EditorOnly/BpTools/**": True,
			"Marvel/Content/Marvel/EditorOnly/Data/**": True,
			"Marvel/Content/Marvel/EditorOnly/FunctionalTest/**": True,
			"Marvel/Content/Marvel/EditorOnly/MRQ/**": True,
			"Marvel/Content/Marvel/EditorOnly/MarvelIcons/**": True,
			"Marvel/Content/Marvel/EditorOnly/ScanCavityData/**": True,
			"Marvel/Content/Marvel/EditorOnly/SherlockEditorTool/**": True,
			"Marvel/Content/Marvel/EditorOnly/SnapFinger/**": True,
			"Marvel/Content/Marvel/EditorOnly/UtilityTool/**": True,
			"Marvel/Content/Marvel/EditorOnly/WwiseEditorTool/**": True,
			"Marvel/Content/Marvel/Effects/**": True,
			"Marvel/Content/Marvel/Environment/**": True,
			"Marvel/Content/Marvel/EnvironmentHydraC/**": True,
			"Marvel/Content/Marvel/Font/**": True,
			"Marvel/Content/Marvel/L10N/**": True,
			"Marvel/Content/Marvel/Maps/**": True,
			"Marvel/Content/Marvel/Movies/**": True,
			"Marvel/Content/Marvel/MoviesBink/**": True,
			"Marvel/Content/Marvel/Movies_Activity/**": True,
			"Marvel/Content/Marvel/Movies_Level/**": True,
			"Marvel/Content/Marvel/Movies_Skin/**": True,
			"Marvel/Content/Marvel/NPC/**": True,
			"Marvel/Content/Marvel/NonAssets/**": True,
			"Marvel/Content/Marvel/NonAssetsToCopy/**": True,
			"Marvel/Content/Marvel/Prototype/**": True,
			"Marvel/Content/Marvel/QAWizardBP/**": True,
			"Marvel/Content/Marvel/ScriptLibs/**": True,
			"Marvel/Content/Marvel/Statistics/**": True,
			"Marvel/Content/Marvel/UI/**": True,
			"Marvel/Content/Marvel/VFX/**": True,
			"Marvel/Content/Marvel/Wwise/**": True
		}
	},
	"extensions": {
		"recommendations": [
			"ms-vscode.cpptools",
			"ms-python.python",
			"ms-python.pylint",
			"ms-python.vscode-pylance",
			"ms-python.autopep8",
			"mjcrouch.perforce"
		]
	},
	"launch": {
		"version": "0.2.0",
		"configurations": [
			{
				"name": "Python: Attach to localhost:5678",
				"type": "debugpy",
				"request": "attach",
				"justMyCode": False,
				"connect": {
					"host": "localhost",
					"port": 5678
				},
				"pathMappings": []
			},
			{
				"name": "Python: Attach to localhost:5678 with script.uep",
				"type": "debugpy",
				"request": "attach",
				"justMyCode": False,
				"connect": {
					"host": "localhost",
					"port": 5678
				},
				"pathMappings": [
					{
						"localRoot": "${workspaceFolder:Scripts}",
						"remoteRoot": "Scripts"
					},
					{
						"localRoot": "${workspaceFolder:Scripts}/../ScriptLibs/Python311/lib/",
						"remoteRoot": "lib"
					},
					{
						"localRoot": "${workspaceFolder:Scripts}/../ScriptLibs/Python311/site-packages/",
						"remoteRoot": "site-packages"
					}
				]
			},
			{
				"name": "Python: Attach - PS4",
				"type": "debugpy",
				"request": "attach",
				"connect": {
					"host": "localhost",
					"port": 5678
				},
				"justMyCode": False,
				"pathMappings": [
					{
						"localRoot": "${workspaceFolder:Scripts}",
						"remoteRoot": "/hostapp/Marvel/Content/Marvel/Scripts"
					}
				]
			},
			{
				"name": "Python: Attach - PS5",
				"type": "debugpy",
				"request": "attach",
				"connect": {
					"host": "localhost",
					"port": 5678
				},
				"justMyCode": False,
				"pathMappings": [
					{
						"localRoot": "${workspaceFolder:Scripts}",
						"remoteRoot": "/host/Marvel/Content/Marvel/Scripts"
					}
				]
			},
			{
				"name": "Python: Attach - Xbox",
				"type": "debugpy",
				"request": "attach",
				"connect": {
					"host": "10.226.179.XXX",
					"port": 5678
				},
				"justMyCode": False,
				"pathMappings": [
					{
						"localRoot": "${workspaceFolder:Scripts}",
						"remoteRoot": "G:/Marvel/Content/Marvel/Scripts"
					}
				]
			}
		]
	}
}

def create_workspace_file(workspace_name, user_name, branch_name, full_path):
	import copy
	workspace_template = copy.deepcopy(WORKSPACE_TEMPLATE)
	absolute_path = os.path.join(full_path, 'UnrealEngine')

	# 动态注入 perforce 用户信息
	workspace_template["settings"]["perforce.user"] = user_name
	workspace_template["settings"]["perforce.client"] = workspace_name

	# 创建文件
	file_name = f"Marvel_{branch_name}.code-workspace"
	file_path = os.path.join(absolute_path, file_name)

	try:
		with open(file_path, "w") as f:
			workspace_json = json.dumps(workspace_template, ensure_ascii=False, indent=4)
			f.write(workspace_json)
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