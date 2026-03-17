def usuario_context(request):
    if request.user.is_authenticated:
        is_func = hasattr(request.user, 'funcionario')
    else:
        is_func = False
        
    return {'is_func': is_func}