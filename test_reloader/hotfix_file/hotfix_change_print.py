def reload_func():
    class new_class:
        def new_print_val():
            print("b")
    print('setattr bbbbb ')
    from class_reloaded import class_reloaded
    setattr(class_reloaded.print_alpha_val, '__code__', new_class.new_print_val.__code__)
    print('setattr bbbbb end')

reload_func()