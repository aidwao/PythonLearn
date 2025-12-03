def outer_function(x):
    y = 10
    z = 20
    
    def inner_function():
        return x + y + z
    
    return inner_function


print(outer_function.__closure__)

# 检查函数是否是闭包
if outer_function.__closure__:
    print("This function is a closure.")
else:
    print("This function is not a closure.")



# 访问闭包的自由变量
if outer_function.__closure__:
    for i, cell in enumerate(nested_closure_ex.__closure__):
        print(f"Free variable {i}: {cell.cell_contents}")
