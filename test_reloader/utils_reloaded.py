"""
    工具方法脚本，由主线程直接调用方法
    后续热更脚本更新该类方法
"""

closure_dict = {"name": "xyc", "age": 18}

def closure_fucn():
    return str(closure_dict["age"])

def get_closure_value():
    name : str = closure_dict["name"]
    return name + closure_fucn()