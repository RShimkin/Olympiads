import os
import subprocess
#import json
import datetime as dt
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
#from django.core.serializers import serialize
from django.db.models import Q

from .forms import *
from .models import *
from .workers import *

def run_cpp(code, lang):
    fname = "main.cpp"
    outname = f"outmain"

    file = open(fname,"w")
    file.write(code)
    file.close()

    command = f"g++ {fname} -o {outname}"
    arr = command.split(' ')
    res = subprocess.run(arr, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    # subprocess.run(arr, capture_output=True, text=True)
    compout = res.stdout.decode('utf-8')
    comperr = res.stderr.decode('utf-8')

    success = True

    if comperr != "":
        print(comperr)

        if "expected" in comperr:
            comperr = "пропущен ожидаемый символ"
        if "not declared in this scope" in comperr:
            comperr = "Странный идентификатор"
        elif "redefinition" in comperr:
            comperr = "Переопределение!"
        elif "abstract declarator" in comperr:
            comperr = "Абстрактный декларатор"
        elif "conversion from" in comperr:
            comperr = "Ошибка приведения типов"
        elif "could not convert" in comperr:
            comperr = "Ошибка приведения к bool"
        elif "statement cannot resolve address of overloaded function" in comperr:
            comperr = "Не хватает скобок при вызове функции"
        elif "is private within this context" in comperr:
            comperr = "Обращение к приватному свойству"
        elif "is not a type" in comperr:
            comperr = "Странный тип..."

        os.remove(fname)
        success = False
        
    return success, fname, outname, compout, comperr

def test_create(code):
    folder = f"{str(dt.datetime.now()).replace(' ','').replace(':','')}"
    os.mkdir(f'works\{folder}')
    fname = f"works\{folder}\main.cpp"
    outname = f"works\{folder}\outmain"

    file = open(fname,"w")
    file.write(code)
    file.close()

    command = f"g++ {fname} -o {outname}"
    arr = command.split(' ')
    res = subprocess.run(arr, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

def test_cpp(code):
    fname = "main.cpp"
    outname = f"outmain"

    file = open(fname,"w")
    file.write(code)
    file.close()

    command = f"g++ {fname} -o {outname}"
    arr = command.split(' ')
    res = subprocess.run(arr, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    # subprocess.run(arr, capture_output=True, text=True)
    compout = res.stdout.decode('utf-8')
    comperr = res.stderr.decode('utf-8')

    success = True

    if comperr != "":

        if "not declared in this scope" in comperr:
            comperr = "Странный идентификатор"
        elif "redefinition" in comperr:
            comperr = "Переопределение!"
        elif "abstract declarator" in comperr:
            comperr = "Абстрактный декларатор"
        elif "conversion from" in comperr:
            comperr = "Ошибка приведения типов"
        elif "could not convert" in comperr:
            comperr = "Ошибка приведения к bool"
        elif "statement cannot resolve address of overloaded function" in comperr:
            comperr = "Не хватает скобок при вызове функции"
        elif "is private within this context" in comperr:
            comperr = "Обращение к приватному свойству"
        elif "is not a type" in comperr:
            comperr = "Странный тип..."

        os.remove(fname)
        success = False
        
    return success, fname, outname, compout, comperr

def run_cs(code, lang):
    fname = "main.cs"
    outname = "main.exe"

    file = open(fname,"w")
    file.write(code)
    file.close()

    command = f"..\CompileCS.cmd {fname}"
    arr = command.split(' ')
    res = subprocess.run(arr, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    # subprocess.run(arr, capture_output=True, text=True)
    compout = res.stdout.decode('CP866')
    comperr = res.stderr.decode('utf-8')

    success = True

    if comperr != "":
        os.remove(fname)
        success = False
        
    return success, fname, outname, compout, comperr

def run_tests(fname, curtask):
    points = 0
    tests = curtask.tests
    input_fname = "args.txt"
    for test in tests:
        inp = test['testinput']
        outp = test['testoutput']

        file = open(input_fname, "w")
        file.write(inp)
        file.close()

        arr = [fname, input_fname]
        res = subprocess.run(arr, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
        out = res.stdout.decode('utf-8')
        err = res.stderr.decode('utf-8')

        if err != "":
            return (False, err, 0)
        
        if out != outp:
            print('outp', outp)
            print('out', out)
        else:
            points += 1
    
    score = (points * curtask.points) // len(tests)

    if os.path.isfile(fname):
        os.remove(fname)
    if os.path.isfile('args.txt'): 
        os.remove('args.txt')

    return (True, "", score)

def tasks(request):
    tasks = Task.objects.filter(Q(olympiadname=None) | Q(olympiadname=''))
    arr = [TaskViewModel(task) for task in tasks]
    return render(request, 'OlympiadMainApp/tasks.html', {'title': 'Список отдельных заданий:','tasks': arr})

def update_task(request, task_name):
    curtask = Task.objects.get(name=task_name)
    if request.method == 'POST':
        form = TestDataForm(request.POST)
        if form.is_valid():
            formcontent = form.cleaned_data
            input =  formcontent['input']
            output = formcontent['output']
            # td = TestData(testinput=input, testoutput=output)
            if isinstance(curtask.tests, list):
                curtask.tests.append({
                    'testinput': input,
                    'testoutput': output
                })
            else:
                curtask.tests = [{
                    'testinput': input,
                    'testoutput': output
                }]
            curtask.save()
        else:
            print('invalid testdata form')
    else:
        form = TestDataForm()
    
    return render(request, 'OlympiadMainApp/updatetask.html', {'task': curtask, 'form': form })

# @login_required(login_url='signup')
@csrf_exempt
def task(request, task_name):
    curtask = Task.objects.get(name=task_name)
    olymp = None
    tmp = curtask.olympiadname
    if tmp != None and tmp != '':
        olymp = Olympiad.objects.get(name=tmp)

    if curtask.creator and curtask.creator == request.user:
        return redirect('updatetask', task_name=curtask.name)

    err = out = comperr = compout = score = ""

    if request.method == 'POST':
        form = CodeForm(request.POST)

        if form.is_valid():
            formcontent = form.cleaned_data
            lang =  formcontent['plang']
            code = formcontent['content']

            if lang == "C++":
                res, cppname, fname, compout, comperr = run_cpp(code, lang)
                fname = f"{fname}.exe"
            elif lang == "C#":
                res, cppname, fname, compout, comperr = run_cs(code, lang)
            
            if res:
                res, err, score = run_tests(fname, curtask)
                if res:
                    if request.user.is_authenticated:
                        un = request.user.username
                        #prevres = Result.objects.filter(taskname=curtask.name).filter(uname = un).first()
                        prevres = curtask.results.filter(uname=un).first()
                        if prevres != None:
                            if score > prevres.points:
                                pts = prevres.points
                                prevres.points = score
                                prevres.save()

                                if olymp != None:
                                    ores = olymp.results.filter(uname=un).first()
                                    if ores == None:
                                        ores = OlympiadResult(
                                            uname = un,
                                            olympiad = olymp.name,
                                            points = score
                                        )
                                        ores.save()
                                        olymp.results.add(ores)
                                        olymp.save()
                                    else:
                                        ores.points += score - pts
                                        ores.save()

                        else:
                            result = TaskResult(
                                uname = un,
                                taskname = curtask.name,
                                points = score,
                            )
                            result.save()
                            curtask.results.add(result)
                            curtask.save()
                            
                            if olymp != None:
                                ores = olymp.results.filter(uname=un).first()
                                if ores == None:
                                    ores = OlympiadResult(
                                        uname = un,
                                        olympiad = olymp.name,
                                        points = score
                                    )
                                    ores.save()
                                    olymp.results.add(ores)
                                    #olymp.save()
                                else:
                                    ores.points += score
                                    ores.save()
                            
                    #
                
            if os.path.isfile(cppname):
                os.remove(cppname)

            table = ''
            if res:
                rating = list(curtask.results.order_by('-points'))
                rating_map = [(i+1,r) for i,r in enumerate(rating)]
                #message = 'Внимание! Аргументы находятся в текстовом файле args.txt'
                table = render(request, 'testcode/ratingtable.html', {'rating': rating_map}).content.decode()

            context = {
                'cerror': comperr, 'cout': compout, 'out': out, 'err': err, 'score': score, 'table': table
            }

            return JsonResponse(context, status=200)
        else:
            print('invalid form')
            return JsonResponse({ 'text': 'invalid form' }, status=400)

    else:
        form = CodeForm()

    rating = list(curtask.results.order_by('-points'))
    rating_map = [(i+1,r) for i,r in enumerate(rating)]
    message = 'Внимание! Аргументы находятся в текстовом файле args.txt'

    return render(request, 'OlympiadMainApp/task.html', {
        'task': curtask, 'title': 'Отправка кода', 'form': form, 
        'cerror': comperr, 'cout': compout, 'out': out, 'err': err, 'score': score, 'rating': rating_map, 'message': message })

def code(request):
    if request.method == 'POST':
        form = MyCodeForm(request.POST)
        if form.is_valid():
            formcontent = form.cleaned_data
            code = formcontent['content']
            lang = formcontent['plang']
            uname = None
            if request.user.is_authenticated:
                uname = request.user.username
            (compil_status, compil_res, prog_name, folder_name) = prepare_program(code, lang, uname)
            if compil_status == prog_statuses.COMPILED_ERR:
                print('compilation error!')
                return JsonResponse({ 'text': 'compilation error!' }, status=400)
            (run_status, run_res) = run_program(prog_name, folder_name, lang)
            if run_status == prog_statuses.RUN_SUC:
                out = run_res.stdout.decode()
                print(out)
                return JsonResponse({ 'text': out }, status=200)
            else:
                print('runtime error!')
                return JsonResponse({ 'text': 'runtime error!' }, status=400)
        else:
            print('invalid form')
    else:
        form = MyCodeForm()

    return render(request, 'OlympiadMainApp/code.html', 
           {'title': 'Отправка кода', 'form': form })

@login_required(login_url='signup')
def create_task(request, olymp_name=None):
    if request.method == 'POST':
        print('post')
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            formcontent = form.cleaned_data
            taskname = formcontent['name']
            taskdescr = formcontent['description']
            taskpoints = formcontent['points']
            taskuntil = formcontent['until']
            taskactive = formcontent['active']
            task = Task()
            task.description = taskdescr
            task.name = taskname
            task.points = taskpoints
            task.until = taskuntil
            task.active = taskactive
            task.slug = taskname
            task.creator = request.user
            task.olympiadname = olymp_name
            task.save()

            if olymp_name != None:
                olymp = Olympiad.objects.get(name=olymp_name)
                print(olymp)
                if olymp != None:
                    try:
                        olymp.tasks.add(task)
                        olymp.save()
                        print('!!success!!')
                    except:
                        print('olymp is wrong!')

            return redirect(task)
        else:
            print('invalid createtask form')
    else:
        form = CreateTaskForm()
    return render(request, 'OlympiadMainApp/createtask.html', {'title': 'Создание задачи', 'form': form, 'olymp': olymp_name })

def olympiads(request):
    olympiads = Olympiad.objects.all()
    arr = [OlympiadViewModel(olymp) for olymp in olympiads]
    return render(request, 'OlympiadMainApp/olympiads.html', {'title': 'Список олимпиад','olympiads': arr})

@login_required(login_url='signup')
def create_olympiad(request):
    if request.method == 'POST':
        form = CreateOlympiadForm(request.POST)
        if form.is_valid():
            cont = form.cleaned_data
            name, descr = cont['name'], cont['description']
            olymp = Olympiad()
            olymp.description, olymp.name, olymp.slug = descr, name, name
            olymp.creator = request.user
            olymp.save()
            return redirect(olymp)
        else:
            print('invalid createtask form')
    else:
        form = CreateOlympiadForm()
    return render(request, 'OlympiadMainApp/createolympiad.html', {'title': 'Создание олимпиады', 'form': form })

# @login_required(login_url='signup')
@csrf_exempt
def olympiad(request, olymp_name):
    olymp = Olympiad.objects.get(name=olymp_name)

    is_creator = False
    cond = True if olymp.creator != None else False
    if cond and olymp.creator == request.user:
        is_creator = True
        #return redirect('update', task_name=curtask.name)
    
    tasks = olymp.tasks.all()
    results = olymp.results.order_by('-points')

    rating = list(olymp.results.all())
    rating_map = [(i+1,r) for i,r in enumerate(results)]

    return render(request, 'OlympiadMainApp/olympiad.html', {
        'olymp': olymp, 'title': 'Олимпиада', 'rating': rating_map, 'is_creator': is_creator, 'tasks': tasks })
