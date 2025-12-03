"""
    单独的类，由主线程调用该类方法
    后续热更脚本更新该类方法
"""
class class_reloaded:
    def print_alpha_val():
        print("a")

    def print_digit_val():
        print("1")

    @staticmethod
    def get_alpha_val():
        return "a"

    def nested_func():
        def bar():
            print(spam)

        spam = 'ham'
        bar()
        spam = 'eggs'
        bar()
        return bar
    
    def test_default_arg(a=1):
        print(a)