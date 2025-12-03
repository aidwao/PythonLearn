import py_compile, marshal, os, typing

if typing.TYPE_CHECKING:
    from io import BufferedReader

def try_to_run_hotfix_file(file : 'BufferedReader'):
    """
    尝试执行目标 pyc
    """
    # 跳过前16个字节的头部信息
    file.seek(16)
    bytecode = file.read()
    # 使用 marshal 序列化再反序列化得到可执行的代码对象
    serialized_bytecode = marshal.dumps(bytecode)
    deserialized_bytecode = marshal.loads(serialized_bytecode)
    code_obj = marshal.loads(deserialized_bytecode)
    eval(code_obj)

skip_file_name_list = ['__init__', __name__]

def run_all_hotfix_in_dir(dir : str = '.'):
    """ 
    找到目标目录下所有的.py文件，编译并在主进程执行 
    默认寻找本目录下所有.py文件
    """
    for file in os.listdir(dir):
        if file.endswith('.py'):
            file_name = file.replace('.py', '')
            if file_name in skip_file_name_list:
                continue
            local_path = os.path.join(dir, file)
            pyc_path = os.path.join(dir, f'{file_name}.pyc')

            py_compile.compile(f'{local_path}', cfile=f'{pyc_path}')
            with open(f"{pyc_path}", 'rb') as f:
                try_to_run_hotfix_file(f)

def update_func(old_func, new_func):
    setattr(old_func, '__code__', new_func.__code__)
    setattr(old_func, '__dict__', new_func.__dict__) # 防止有使用方法属性cache数据
    setattr(old_func, '__defaults__', new_func.__defaults__)
    setattr(old_func, '__kwdefaults__', new_func.__kwdefaults__)