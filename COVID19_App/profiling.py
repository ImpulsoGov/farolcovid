import cProfile, io, pstats

def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        result = func(*args, **kwargs)
        
        pr.disable()
        # pr.dump_stats('log.profile')
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
        ps.print_stats(5)
        print(s.getvalue())
        
        return result
    
    return profiled_func


##==>>> HOW TO READ PROFILE DATA
# import pstats
# p = pstats.Stats('profile_dump')
# # skip strip_dirs() if you want to see full path's
# p.strip_dirs().print_stats()