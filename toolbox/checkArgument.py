
def checkArgument(opt, dict, default = False):
    if dict is None:
        return default
    if not opt in dict:
        return default
    else: return dict[opt]

