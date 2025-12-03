def reload_func():
    def new_get_closure_value():
        name : str = "newname"
        return name + closure_fucn()
    print('hotfix new_get_alpha_val start')
    import reloader_utils
    import utils_reloaded
    reloader_utils.update_func(utils_reloaded.get_closure_value, new_get_closure_value)
    print('hotfix new_get_alpha_val end')

reload_func()