from enum import Enum

class prog_langs(Enum):
    CPP = "C++"
    PYTHON = "Python"

    @classmethod
    def choices(cls):
        #print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)

def get_processor(pg):
    if pg == prog_langs.CPP.name:
        return cpp_processor()
    elif pg == prog_langs.PYTHON.name:
        return python_processor()
    else:
        print('wtf:',pg)
        return None

class cpp_processor:
    def compile_str(self, source_fname, target_fname):
        return f"g++ {source_fname} -o {target_fname}"
    
    def run_str(self, fname):
        return f"./{fname}"
    
    def fname_ext(self, fname):
        return f"{fname}.cpp"
    
    def need_compilation(self):
        return True
    
class python_processor:
    def compile_str(self, source_fname, target_fname):
        return None
    
    def run_str(self, fname):
        return f"python3 {fname}"
    
    def fname_ext(self, fname):
        return f"{fname}.py"
    
    def need_compilation(self):
        return False