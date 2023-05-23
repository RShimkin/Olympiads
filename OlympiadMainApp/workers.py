import datetime as dt
import os
import subprocess as sp

from .langs import *
from .models import *

class prog_statuses(Enum):
    SAVED_SUC = "saved in file"
    COMPILED_SUC = "successfully compiled"
    COMPILED_ERR = "compilation error"
    COMPILE_NO = "interpretable"
    RUN_SUC = "run successfully"
    RUN_ERR = "runtime error"

def prepare_program(code, lang, uname):
    lang_processor = get_processor(lang)

    (save_status, folder_name, code_file_name) = save_code(code=code, processor=lang_processor, username=uname)

    (compile_status, compile_result, prog_name) = compile_code(folder=folder_name, code=code_file_name, processor=lang_processor)

    return (compile_status, compile_result, prog_name, folder_name)
    
    #res = sp.run(command.split(' '), stdout = sp.PIPE, stderr = sp.PIPE)
    #print(res.stdout.decode())

def run_program(prog, folder, lang, testinput=None):

    lang_processor = get_processor(lang)

    if testinput != None:
        pass

    result = run_code(folder, prog, lang_processor)

    return result

def remove_program(code_name = None, prog_name = None):
    if code_name != None and os.path.isfile(code_name):
        os.remove(code_name)
    if prog_name != None and os.path.isfile(prog_name):
        os.remove(prog_name)

def save_code(code, processor, username):
    print(code)
    print(username)
    fname = str(dt.datetime.now()).replace(' ','').replace(':','').replace('.','')
    folder = "processing"
    if username != None:
        fname = "main"
        folder = f"processing/{username}"
        print(folder)
        if not os.path.isdir(folder):
            os.mkdir(folder)

    code_name = f"{folder}/{processor.fname_ext(fname)}"

    file = open(code_name,"w")
    file.write(code)
    file.close()

    return (prog_statuses.SAVED_SUC, folder, fname)

def compile_code(folder, code, processor):
    if processor.need_compilation():
        full_code_name = f"{folder}/{processor.fname_ext(code)}"
        full_prog_name = f"{folder}/{code}"
        command = processor.compile_str(source_fname=full_code_name, target_fname=full_prog_name) #f"g++ {codename} -o processing/{progname}"
        arr = command.split(' ')
        result = sp.run(arr, stdout = sp.PIPE, stderr = sp.PIPE)
        #print(res.stdout.decode())
        #print(res.stderr.decode())
        if result.stderr.decode() == "":
            return (prog_statuses.COMPILED_SUC, result, code)
        else:
            return (prog_statuses.COMPILED_ERR, result, code)
    else:
        return (prog_statuses.COMPILE_NO, None, processor.fname_ext(code))
    
def run_code(folder, prog, processor):
    firejail_str = f"firejail --seccomp --quiet --blacklist=/ --private=./{folder}"
    command = f"{firejail_str} {processor.run_str(prog)}"
    res = sp.run(command.split(' '), stdout = sp.PIPE, stderr = sp.PIPE)
    status = prog_statuses.RUN_SUC
    if res.stderr.decode():
        status = prog_statuses.RUN_ERR
    return (status, res)
