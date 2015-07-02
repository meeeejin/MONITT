from django.shortcuts import render, render_to_response, RequestContext
from django.http import HttpResponseRedirect
from forms import UploadFileForm
from models import UploadFile
from django.core.urlresolvers import reverse
from django.contrib import auth
import os, ast, json, yaml

from django.db.models import Q
from models import ActualResponses, ExpectedResponses, Notifications, Requests, Results, TestHistory, Schedulings

# Create your views here.
test_path = os.getcwd()
filepath = test_path + '/../static/media/files'

def alltestresults_search(request):
    data = search(request, 0)
    template = 'alltestresults_search.html'
    
    if request.is_ajax():
        template = 'alltestresults_search_page.html'
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def alltests_search(request):
    data = search(request, 4)
    template = 'alltests_search.html'
    
    if request.is_ajax():
        template = 'alltests_search_page.html'
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def schedulings_search(request):
    data = search(request, 1)
    template = 'schedulings_search.html'
    
    if request.is_ajax():
        template = 'schedulings_search_page.html'
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def notifications_search(request):
    data = search(request, 2)
    template = 'notifications_search.html'
    
    if request.is_ajax():
        template = 'notifications_search_page.html'
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def errors_search(request):
    data = search(request, 3)
    template = 'errors_search.html'
    
    if request.is_ajax():
        template = 'errors_search_page.html'
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def search(request, option):
    username = auth_check(request)
    
    data = {}
    testslist = []
    error_check = 0
    
    query = request.GET['q']
    
    try:
        if option==0:
            alltestid = TestHistory.objects.filter(Q(testcase_name__icontains=query)).values_list('test_id', flat=True)
            testsnum = len(alltestid)

            for i in range(1, testsnum):
                testinfo = abstract_testinfo(alltestid, i)
                testslist.append(testinfo)
        elif option==1:
            alltestcaseid = Schedulings.objects.filter(Q(testcase_name__icontains=query)).values_list('testcase_id', flat=True)
            testcasenum = len(alltestcaseid)
        
            for i in range(0, testcasenum):
                alltestid = TestHistory.objects.filter(testcase_id=alltestcaseid[i]).values_list('test_id', flat=True)
                testnum = len(alltestid)
                
                if testnum != 0:
                    testcaseinfo = abstract_scheduling_info(alltestcaseid[i])
                    testlist = []
                    testlist.append(testcaseinfo)
                    for j in range(0, testnum):
                        testinfo = abstract_testinfo(alltestid, j)
                        testlist.append(testinfo)
                    testslist.append(testlist)
        elif option==2:
            alltestcaseid = Notifications.objects.filter(Q(testcase_name__icontains=query)).values_list('testcase_id', flat=True)
            testcasenum = len(alltestcaseid)

            for i in range(0, testcasenum):
                alltestid = TestHistory.objects.filter(testcase_id=alltestcaseid[i]).values_list('test_id', flat=True)
                testnum = len(alltestid)
                if testnum != 0:
                    testcaseinfo = abstract_notification_info(alltestcaseid[i])
                    testlist = []
                    testlist.append(testcaseinfo)
                    for j in range(0, testnum):
                        testinfo = abstract_testinfo(alltestid, j)
                        testlist.append(testinfo)
                    testslist.append(testlist)
        elif option==3:
            alltestid = TestHistory.objects.filter(Q(testcase_name__icontains=query)).values_list('test_id', flat=True)
            testnum = len(alltestid)

            for i in range(0, testnum):
                testresult = Results.objects.filter(test_id=alltestid[i]).values_list('result', flat=True)
                if len(testresult) != 0:
                    if testresult[0] == 'FAIL':
                        testinfo = abstract_testinfo(alltestid, i)
                        testslist.append(testinfo)
        elif option==4:
            filenamelist = []
    
            for dir_entry in os.listdir(filepath):
                dir_entry_path = os.path.join(filepath, dir_entry)
                fileExtension = os.path.splitext(dir_entry_path)[1]
                fname = os.path.basename(dir_entry_path)
                if query in fname:
                    if os.path.isfile(dir_entry_path) and fileExtension == '.json':
                        with open(dir_entry_path, 'r') as testfile:
                            f = testfile.read()
                            f = f.replace('\t', '')
                            testslist.append(f)
                            filenamelist.append(fname)
                
            data['filenamelist'] = filenamelist
    
        testslist = list(reversed(testslist))
        
    except:
        error_check = 1

    data['testslist'] = testslist
    data['username'] = username
    data['query'] = query
    data['error'] = error_check
    
    return data

def delete_test(request):
    testid = request.GET['test_id']
    TestHistory.objects.filter(test_id=testid).delete()
    
    return HttpResponseRedirect("/dashboard/")

def delete_noti(request):
    notiid = request.GET['noti_id']
    Notifications.objects.filter(notification_id=notiid).delete()
    
    return HttpResponseRedirect("/dashboard/notification_tests/")

def delete_sche(request):
    scheid = request.GET['sche_id']
    Schedulings.objects.filter(scheduling_id=scheid).delete()
    
    return HttpResponseRedirect("/dashboard/scheduling_tests/")

def delete_file(request):
    filename = request.GET['filename']
    filename = filename + ".json"
    abs_filepath = os.path.join(filepath, filename)
    os.remove(abs_filepath)
    
    return HttpResponseRedirect("/dashboard/alltests/")

def run_test(request):
    filename = request.GET['filename']
    filename = filename + '.json'
    abs_filepath = os.path.join(filepath, filename)
    
    command = "/usr/bin/python " + test_path + "/dashboard/testsrc/main.py " + abs_filepath
    os.system(command)
    
    return HttpResponseRedirect("/dashboard/alltests/")

def auth_check(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username
        
    return username

def abstract_testinfo(alltestid, i):
    testinfo = []
    testinfo.append(TestHistory.objects.filter(test_id=alltestid[i]).values_list('testcase_name', flat=True)[0])
    testinfo.append(Requests.objects.filter(test_id=alltestid[i]).values_list('method', flat=True)[0])
    testinfo.append(Requests.objects.filter(test_id=alltestid[i]).values_list('url', flat=True)[0])
    
    testinfo.append(alltestid[i])
    
    testinfo.append(ast.literal_eval(Requests.objects.filter(test_id=alltestid[i]).values_list('url_parameter', flat=True)[0]))
    testinfo.append(ast.literal_eval(Requests.objects.filter(test_id=alltestid[i]).values_list('header', flat=True)[0]))
    testinfo.append(ast.literal_eval(Requests.objects.filter(test_id=alltestid[i]).values_list('body', flat=True)[0]))
    
    testinfo.append(ExpectedResponses.objects.filter(test_id=alltestid[i]).values_list('return_code', flat=True)[0])
    testinfo.append(ExpectedResponses.objects.filter(test_id=alltestid[i]).values_list('response_time', flat=True)[0])
    testinfo.append(ast.literal_eval(ExpectedResponses.objects.filter(test_id=alltestid[i]).values_list('header', flat=True)[0]))
    testinfo.append(ast.literal_eval(ExpectedResponses.objects.filter(test_id=alltestid[i]).values_list('body', flat=True)[0]))
    
    testinfo.append(ActualResponses.objects.filter(test_id=alltestid[i]).values_list('return_code', flat=True)[0])
    testinfo.append(ActualResponses.objects.filter(test_id=alltestid[i]).values_list('response_time', flat=True)[0])
    testinfo.append(ast.literal_eval(ActualResponses.objects.filter(test_id=alltestid[i]).values_list('header', flat=True)[0]))
    testinfo.append(ast.literal_eval(ActualResponses.objects.filter(test_id=alltestid[i]).values_list('body', flat=True)[0]))
    
    testinfo.append(Results.objects.filter(test_id=alltestid[i]).values_list('result', flat=True)[0])
    testinfo.append(Results.objects.filter(test_id=alltestid[i]).values_list('error_list', flat=True)[0].split(" ||| "))
    testinfo.append(Results.objects.filter(test_id=alltestid[i]).values_list('finished_time', flat=True)[0])
    
    return testinfo

def abstract_scheduling_info(testcaseid):
    testcaseinfo = []

    testcaseinfo.append(Schedulings.objects.filter(testcase_id=testcaseid).values_list('method', flat=True)[0])
    testcaseinfo.append(Schedulings.objects.filter(testcase_id=testcaseid).values_list('frequency', flat=True)[0])
    testcaseinfo.append(Schedulings.objects.filter(testcase_id=testcaseid).values_list('times', flat=True)[0])
    testcaseinfo.append(Schedulings.objects.filter(testcase_id=testcaseid).values_list('testcase_name', flat=True)[0])
    testcaseinfo.append(Schedulings.objects.filter(testcase_id=testcaseid).values_list('request_method', flat=True)[0])
    testcaseinfo.append(Schedulings.objects.filter(testcase_id=testcaseid).values_list('request_url', flat=True)[0])
    testcaseinfo.append(Schedulings.objects.filter(testcase_id=testcaseid).values_list('register_time', flat=True)[0])
    testcaseinfo.append(Schedulings.objects.filter(testcase_id=testcaseid).values_list('scheduling_id', flat=True)[0])
    
    return testcaseinfo

def abstract_notification_info(testcaseid):
    testcaseinfo = []
    
    testcaseinfo.append(Notifications.objects.filter(testcase_id=testcaseid).values_list('notification_type', flat=True)[0])
    testcaseinfo.append(Notifications.objects.filter(testcase_id=testcaseid).values_list('fail_count', flat=True)[0])
    testcaseinfo.append(Notifications.objects.filter(testcase_id=testcaseid).values_list('success_count', flat=True)[0])
    testcaseinfo.append(Notifications.objects.filter(testcase_id=testcaseid).values_list('total_count', flat=True)[0])
    testcaseinfo.append(Notifications.objects.filter(testcase_id=testcaseid).values_list('notification_count', flat=True)[0])
    testcaseinfo.append(Notifications.objects.filter(testcase_id=testcaseid).values_list('register_time', flat=True)[0])
    testcaseinfo.append(Notifications.objects.filter(testcase_id=testcaseid).values_list('notification_id', flat=True)[0])
    
    return testcaseinfo

def dashboard(request, template='all_test_results.html', page_template='all_test_results_page.html'):
    data = {}
    testlist = []
    username = auth_check(request)

    alltestid = TestHistory.objects.filter(user_id=username).values_list('test_id', flat=True)
    testnum = len(alltestid)
    
    for i in range(0, testnum):
        testinfo = abstract_testinfo(alltestid, i)
        testlist.append(testinfo)
        
    testlist = list(reversed(testlist))

    data['testlist'] = testlist
    data['username'] = username
    data['page_template'] = page_template
    
    if request.is_ajax():
        template = page_template
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def alltests(request, template='alltests.html', page_template='alltests_page.html'):
    username = auth_check(request)
    
    data = {}
    filelist = []
    filenamelist = []
    
    for dir_entry in os.listdir(filepath):
        dir_entry_path = os.path.join(filepath, dir_entry)
        fileExtension = os.path.splitext(dir_entry_path)[1]
        if os.path.isfile(dir_entry_path) and fileExtension == '.json':
            with open(dir_entry_path, 'r') as testfile:
                f = testfile.read()
                f = f.replace('\t', '')
                filelist.append(f)
                base = os.path.basename(dir_entry_path)
                filenamelist.append(os.path.splitext(base)[0])
        
    data['filelist'] = filelist
    data['username'] = username
    data['filenamelist'] = filenamelist
    
    if request.is_ajax():
        template = page_template
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def create_test(request):
    username = auth_check(request)
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            testfile=request.FILES['testfile']
            new_file = UploadFile(testfile=request.FILES['testfile'])
            new_file.save()
            command = "/usr/bin/python " + test_path + "/dashboard/testsrc/main.py " + test_path + "/../static/media/files/" + testfile.name
            os.system(command)
            return HttpResponseRedirect(reverse('dashboard.views.create_test'))
    else:
        form = UploadFileForm()
        
    data = {'form': form}
    
    return render_to_response("create_test.html", locals(), context_instance=RequestContext(request))

def notification_tests(request, template='notification_tests.html', page_template='notification_test_page.html'):
    username = auth_check(request)
    
    data = {}
    testcaselist = []

    alltestcaseid = Notifications.objects.filter(user_id=username).values_list('testcase_id', flat=True)
    testcasenum = len(alltestcaseid)
    
    for i in range(0, testcasenum):
        alltestid = TestHistory.objects.filter(testcase_id=alltestcaseid[i]).values_list('test_id', flat=True)
        testnum = len(alltestid)
        testcaseinfo = abstract_notification_info(alltestcaseid[i])
        testlist = []
        testlist.append(testcaseinfo)
        for j in range(0, testnum):
            testinfo = abstract_testinfo(alltestid, j)
            testlist.append(testinfo)
        testcaselist.append(testlist)

    testcaselist = list(reversed(testcaselist))

    data['testcaselist'] = testcaselist
    data['username'] = username
    
    if request.is_ajax():
        template = page_template
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def errors(request, template='errors.html', page_template='errors_page.html'):
    username = auth_check(request)
    
    data = {}
    testlist = []

    alltestid = TestHistory.objects.filter(user_id=username).values_list('test_id', flat=True)
    testnum = len(alltestid)
    
    for i in range(0, testnum):
        testresult = Results.objects.filter(test_id=alltestid[i]).values_list('result', flat=True)
        if testresult[0] == 'FAIL':
            testinfo = abstract_testinfo(alltestid, i)
            testlist.append(testinfo)
            
    testlist = list(reversed(testlist))

    data['testlist'] = testlist
    data['username'] = username
    
    if request.is_ajax():
        template = page_template
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def scheduling_tests(request, template='scheduling_tests.html', page_template='scheduling_test_page.html'):
    username = auth_check(request)
    
    data = {}
    testcaselist = []

    alltestcaseid = Schedulings.objects.filter(user_id=username).values_list('testcase_id', flat=True)
    testcasenum = len(alltestcaseid)
    
    for i in range(0, testcasenum):
        alltestid = TestHistory.objects.filter(testcase_id=alltestcaseid[i]).values_list('test_id', flat=True)
        testnum = len(alltestid)
        testcaseinfo = abstract_scheduling_info(alltestcaseid[i])
        testlist = []
        testlist.append(testcaseinfo)
        for j in range(0, testnum):
            testinfo = abstract_testinfo(alltestid, j)
            testlist.append(testinfo)
        testcaselist.append(testlist)

    testcaselist = list(reversed(testcaselist))

    data['testcaselist'] = testcaselist
    data['username'] = username
    
    if request.is_ajax():
        template = page_template
    
    return render_to_response(template, data, context_instance=RequestContext(request))

def guide(request):
    username = auth_check(request)
    
    return render_to_response("guide.html",locals(), context_instance=RequestContext(request))

def settings(request):
    username = auth_check(request)
    
    return render_to_response("settings.html",locals(), context_instance=RequestContext(request))

def signout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")