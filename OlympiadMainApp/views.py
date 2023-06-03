import os
import subprocess
#import json
from bson import ObjectId
import datetime as dt
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
#from django.core.serializers import serialize
from django.db.models import Q

from .forms import *
from .models import *
from .workers import *
from .config import Config

from OlympiadUsers.access import *

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
    #tasks = StandaloneTask.objects.all()
    #tasks = StandaloneTask.objects.exclude(Q(creator=request.user) & Q(hidden=True))
    if request.user.is_authenticated:
        tasks = StandaloneTask.objects.exclude(creator=request.user)
        own_tasks = StandaloneTask.objects.filter(creator=request.user)
    else:
        tasks = StandaloneTask.objects.all()
        own_tasks = []
    tasks_arr = [StandaloneTaskViewModel(task) for task in tasks]
    own_arr = [StandaloneTaskViewModel(task) for task in own_tasks]
    own_exist = len(own_arr) > 0
    allow_create = has_groups(request.user, 'Creators')
    #print(request.user.groups)
    return render(request, 'OlympiadMainApp/standalonetasks.html',
                   {'title': 'Список отдельных заданий:', 'allow_create': allow_create,
                    'tasks': tasks_arr, 'own_tasks': own_arr, 'own_exist': own_exist })

'''
def tasks2(request):
    tasks = Task.objects.filter(Q(olympiadname=None) | Q(olympiadname=''))
    arr = [TaskViewModel(task) for task in tasks]
    allow_create = has_groups(request.user, 'Creators')
    return render(request, 'OlympiadMainApp/tasks.html', {'title': 'Список отдельных заданий:','tasks': arr, 'allow_create': allow_create})
'''

'''
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
    
    return render(request, 'OlympiadMainApp/updatetask.html', {'task': curtask, 'form': form })'''

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
                remove_program(folder_name, None, prog_name)
                return JsonResponse({ 'text': 'compilation error!', 'error': True }, status=200)
            (run_status, run_res) = run_program(prog_name, folder_name, lang)
            remove_program(folder_name, None, prog_name)
            if run_status == prog_statuses.RUN_SUC:
                out = run_res.stdout.decode()
                print(out)
                return JsonResponse({ 'text': out, 'error': False }, status=200)
            elif run_status == prog_statuses.RUN_TOE:
                return JsonResponse({ 'text': 'timeout violation', 'error': True }, status=200)
            else:
                print('runtime error!')
                return JsonResponse({ 'text': 'runtime error!', 'error': True }, status=200)
        else:
            print('invalid form')
    else:
        form = MyCodeForm()

    return render(request, 'OlympiadMainApp/code.html', 
           {'title': 'Отправка кода', 'form': form })

@group_required_or_anon('Participants')
def stask(request, task_oid):
    curtask = StandaloneTask.objects.get(_id=ObjectId(task_oid))
    now = dt.datetime.now().astimezone(curtask.since.tzinfo)
    form = CodeForm(request.POST or None)
    #print(request.META.get("REMOTE_ADDR"))
    if form.is_valid():
        if request.user.is_authenticated:
            tr = curtask.results.filter(user=request.user).first()
        else:
            tr = curtask.results.filter(username=str(request.META.get("REMOTE_ADDR"))).first()
        print(tr)
        if not tr:
            print("StandaloneTaskResult not found")
            return JsonResponse({'text': 'Ошибка сессии', 'error': True}, status=200)
        tr.inner_attempts += 1
        tr.save()
        formcontent = form.cleaned_data
        code, lang = formcontent['content'], formcontent['plang']
        uname = request.user.username if request.user.is_authenticated else None

        (compil_status, compil_res, prog_name, folder_name) = prepare_program(code, lang, uname)
        if compil_status == prog_statuses.COMPILED_ERR:
            return JsonResponse({ 'text': 'Ошибка компиляции!', 'error': True }, status=200)

        run_status, match = prog_statuses.RUN_SUC, True
        for test in curtask.tests:
            inp, out = test['testinput'], test['testoutput']
            input_file_name = f"{folder_name}/input.txt"
            output_file_name = f"{folder_name}/output.txt"
            file = open(input_file_name, 'w')
            file.write(inp)
            file.close()
            (run_status, run_res) = run_program(prog_name, folder_name, lang)
            if run_status != prog_statuses.RUN_SUC:
                break
            res = run_res.stdout.decode('utf-8')
            if os.path.isfile(output_file_name):
                file = open(output_file_name, "r")
                res = file.read()
                file.close()
            if res.strip() != out.strip():
                match = False
                break

        remove_program(folder_name, input_file_name, None)
        remove_program(folder_name, output_file_name, None)
        remove_program(folder_name, None, prog_name)

        if not match:
            return JsonResponse({ 'text': 'Неверный результат работы программы', 'error': True }, status=200)
        if run_status == prog_statuses.RUN_ERR:
            return JsonResponse({ 'text': 'Ошибка времени выполнения!', 'error': True }, status=200)
        if run_status == prog_statuses.RUN_TOE:
            return JsonResponse({ 'text': 'Слишком долгое выполнения!', 'error': True }, status=200)

        tr.finished = now
        tr.points = curtask.points
        tr.success = True
        curtask.results_number += 1
        tr.save()
        curtask.save()
        return JsonResponse({ 'text': 'Тесты успешно пройдены!', 'error': False }, status=200)
    if request.user.is_authenticated:
        tr = curtask.results.filter(user=request.user).first()
        if not tr:
            tr = StandaloneTaskResult(taskname=str(curtask._id), success=False,
                points=0, attempts=1, inner_attempts=0, started=now, 
                finished=curtask.until, user=request.user, username=request.user.username)
            tr.save()
            curtask.results.add(tr)
            curtask.save()
    else:
        tr = curtask.results.filter(username=str(request.META.get("REMOTE_ADDR"))).first()
        if not tr:
            tr = StandaloneTaskResult(taskname=str(curtask._id), success=False,
                points=0, attempts=1, inner_attempts=0, started=now, finished=curtask.until,
                username=request.META.get("REMOTE_ADDR"))
            tr.save()
            curtask.results.add(tr)
            curtask.save()
    print(tr)
    #message = 'Внимание! Аргументы находятся в текстовом файле args.txt'
    return render(request, 'OlympiadMainApp/stask.html', {
        'task': curtask, 'title': 'Отправка кода', 'form': form, 'oid': task_oid
        #'cerror': comperr, 'cout': compout, 'out': out, 'err': err, 'score': score, 'rating': rating_map, 'message': message 
        })

@login_required(login_url='login')
@group_required('Creators')
def update_task(request, task_oid):
    curtask = StandaloneTask.objects.get(_id=ObjectId(task_oid))
    if request.method == 'POST':
        form = SimpleCodeTestDataForm(request.POST)
        if form.is_valid():
            formcontent = form.cleaned_data
            input, output =  formcontent['input'], formcontent['output']
            td = TestData(testinput=input, testoutput=output)
            if isinstance(curtask.tests, list):
                curtask.tests.append(td)
            else:
                curtask.tests = [td]
            curtask.save()
        else:
            print('invalid testdata form')
    else:
        form = SimpleCodeTestDataForm()
    
    return render(request, 'OlympiadMainApp/updatetask.html', {'task': curtask, 'form': form, 'oid': task_oid })

@login_required(login_url='login')
@group_required('Creators')
def edit_stask(request, task_oid):
    task = StandaloneTask.objects.get(_id=ObjectId(task_oid))
    form = EditStaskForm(request.POST or None, instance=task)
    testdataform = SimpleCodeTestDataForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
    if testdataform.is_valid():
        print(testdataform.cleaned_data)
    #return JsonResponse({'taskname': task.name}, status=200)
    return render(request, 'OlympiadMainApp/editstask.html', {'form': form, 'oid': task_oid, 'testdataform': testdataform })

def view_stask(request, task_oid):
    task = StandaloneTask.objects.get(_id=ObjectId(task_oid))
    #rating = list(task.results.order_by('-points'))
    results = [StandaloneTaskResultViewModel(res) for res in task.results.filter(points__gt=0)]
    results.sort(key=lambda x: x.time)
    #rating_map = [(i+1, StandaloneTaskResultViewModel(r)) for i,r in enumerate(task.results.filter(points__gt=0))]
    rating_map = [(i+1, r) for i,r in enumerate(results)]
    #rating_map.sort(key=lambda tup: tup[1].time)
    return render(request, 'OlympiadMainApp/viewstask.html', {'task': task, 'oid': task_oid, 'rating': rating_map})

@login_required(login_url='login')
@group_required('Creators')
def create_stask(request):
    form = CreateTaskForm(request.POST or None)
    if form.is_valid():
        task = stask_from_form_data(form, request.user)
        task.save()
        return redirect('editstask', task_oid=str(task._id))
    return render(request, 'OlympiadMainApp/createtask.html', {'title': 'Создание задачи', 'form': form })

def stask_from_form_data(form, user):
    d = form.cleaned_data
    task = StandaloneTask()
    task.name, task.description, task.short_description = d['name'], d['description'], d['short_description']
    task.points = Config().STANDALONE_POINTS
    task.since, task.until, task.tasktype = d['since'], d['until'], d['tasktype']
    now = datetime.now().astimezone(task.since.tzinfo)
    if task.since <= now:
        task.active = True
    else:
        task.active = False
    task.creator = user
    task.created = now
    return task

"""

# @login_required(login_url='signup')
@csrf_exempt
def task(request, task_oid):
    curtask = Task.objects.get(name=task_oid)
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


@login_required(login_url='login')
@group_required('Creators')
def create_task2(request, olymp_name=None):
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
        form = CreateTaskForm2()
    return render(request, 'OlympiadMainApp/createtask2.html', {'title': 'Создание задачи', 'form': form, 'olymp': olymp_name })

def olympiads(request):
    olympiads = Olympiad.objects.all()
    arr = [OlympiadViewModel(olymp) for olymp in olympiads]
    allow_create = has_groups(request.user, 'Creators')
    return render(request, 'OlympiadMainApp/olympiads.html', {'title': 'Список олимпиад','olympiads': arr, 'allow_create': allow_create})

@login_required(login_url='signup')
@group_required('Creators')
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
"""

def test(request):
    value = request.session.get("test", 0)
    if value <= 0:
        request.session['test'] = 1
    request.session['test'] = value+1
    return JsonResponse({'times': request.session['test']}, status = 200)

def filetest(request):
    if request.method == "POST":
        print(request.POST)
        print(request.FILES)
        file = request.FILES['file']
        path = default_storage.save('heart_of_the_swarm.txt', ContentFile(file.read()))
        print(path)
    form = FileTestForm(request.POST or None)
    #print(form.file)
    return render(request, 'OlympiadMainApp/testfile.html', {'form': form})
