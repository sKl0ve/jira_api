import json
import numpy as np
import requests
import seaborn as sns
import datetime
import matplotlib.pyplot as plt
from collections import Counter
#from datetime import datetime, timedelta, date


def convert_time(timestring):
    timestring_cut = timestring.split('.')[0]
    timestring_date = timestring_cut.split('T')[0]
    timestring_time = timestring_cut.split('T')[1]
    timestring = timestring_date + ' ' + timestring_time
    time = datetime.datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S')
    return time


def creating_problem_time(df):
    creating_time = df['fields']['created']
    time = convert_time(creating_time)
    return time


def solving_problem_time(df):
    resolution_datetime = df['fields']['resolutiondate']
    time = convert_time(resolution_datetime)
    return time


def summ_elements(list):
    list_summ = []
    s = 0
    for elem in list:
        s = s + elem
        list_summ.append(s)
    return list_summ


def calculating_time_spent_on_status(dataset):
    status_open_time = datetime.timedelta(0)
    status_in_progress_time =  datetime.timedelta(0)
    status_resolved_time =  datetime.timedelta(0)
    status_reopened_time =  datetime.timedelta(0)
    status_closed_time =  datetime.timedelta(0)
    
    start_time = creating_problem_time(dataset)
    for df in dataset['changelog']['histories']:
        for el in df['items']:
            if el['field'] == 'status':
                end_time = convert_time(df['created'])
                time_spent = end_time - start_time
                status = el['fromString']
                if status == 'Open':
                    status_open_time = status_open_time + time_spent
                elif status == 'In Progress':
                    status_in_progress_time = status_in_progress_time + time_spent
                elif status == 'Resolved':
                    status_resolved_time = status_resolved_time + time_spent
                elif status == 'Reopened':
                    status_reopened_time = status_reopened_time + time_spent
                elif status == 'Closed':
                    status_closed_time = status_closed_time + time_spent
                start_time = end_time
    return status_open_time, status_in_progress_time, status_resolved_time, status_reopened_time, status_closed_time

                  
def get_resolved_time_for_assignee(issue, username):
    l_start = get_issue_item_to_time(issue, 'assignee', username)
    if l_start == []:
        time_start = creating_problem_time(issue)
    else:
        time_start = l_start[-1]

    l_stop = get_issue_item_to_time(issue, 'status', 'Resolved')
    if l_stop == []:
        time_stop = solving_problem_time(issue)
    else:
        time_stop = l_stop[-1]

    answer = (time_stop - time_start).total_seconds // 3600
    return answer                

      
def get_issue_item_to_time(issue, field, to):
    time_list = []
    for history in issue['changelog']['histories']:
        for item in history['items']:
            if item['field'] == field and (item['toString'] == to or item['to'] == to):
                time_list.append(convert_time(history['created']))
    return time_list


def time_to_solve_the_issue():
    filtered = {'jql' : 'project=Ace AND status=Closed ORDER BY created', 'maxResults' : '100',
              'expand' : 'changelog',
              'fields' : 'created,resolutiondate'} 

    response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=filtered)
    dataset = json.loads(response.text)
    
    time_spent = []
    for df in dataset['issues']:
        time = (solving_problem_time(df) - creating_problem_time(df)).days
        time_spent.append(time)
    
    sns.histplot(time_spent, kde=True, color='lightgreen', edgecolor='red', bins=10)
    plt.xlabel("Затраченное время (в днях)")
    plt.ylabel("Количество задач")
    plt.title("Время, которое задача провела в открытом состоянии")
    plt.show()


def make_lists_name_num(list_users, count):
    counted_values = Counter(list_users)
    arr = counted_values.most_common(count)
    list_names = []
    list_nums = []
    for elem in arr:
        list_names.append(elem[0])
        list_nums.append(elem[1])
    return list_names, list_nums


def distribution_of_time_by_tasks():
    filtered = {'jql' : 'project=Kafka AND status=Closed ORDER BY created', 'maxResults' : '1000',
              'expand' : 'changelog',
              'fields' : 'created'}
    
    response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=filtered)
    dataset = json.loads(response.text)
    
    status_open_list = []
    status_in_progress_list = []
    status_resolved_list = []
    status_reopened_list = []
    status_close_list = []
    
    lists = [status_open_list, status_in_progress_list, status_resolved_list, status_reopened_list, status_close_list]
    
    for df in dataset['issues']:
        time_opened, time_in_progress, time_resolved, time_reopened, time_closed = calculating_time_spent_on_status(df)
        time_list = [time_opened, time_in_progress, time_resolved, time_reopened, time_closed]
        for i in range(len(lists)):
            if time_list[i] != datetime.timedelta(0):
                lists[i].append(time_list[i].seconds // 60)
    
    status_list = ['Open', 'In progress', 'Resolved', 'Reopened', 'Close']
    
    for i in range(len(lists)):
        sns.histplot(lists[i], kde=True, color='lightgreen', edgecolor='red', bins=50)
        plt.xlabel("Затраченное время (в часах)")
        plt.ylabel("Количество задач")
        plt.title(f"Время, которое задачи провели в статусе {status_list[i]}")
        plt.show()


def opened_and_closed_issues_per_day():
    PERIOD = 30 
    opened_issues_list = []
    date_list = []
    current_date = datetime.date.today()
    
    for i in range(PERIOD, -1, -1):
        date = current_date - datetime.timedelta(i)
        filtered = {'jql': f'project=OAK AND created >= "{date}" AND created < "{date + datetime.timedelta(1)}"',
                    'maxResults' : '100', 'fields' : 'created'}
        date_list.append(date.strftime("%d") + '.' + date.strftime("%m"))
        response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=filtered)
        dataset = json.loads(response.text)
        opened_issues_list.append(dataset['total'])
        
    plt.plot(opened_issues_list, linewidth=3.0, color='grey')
    
    close_list_dates = []
    payload = {'jql': f'project=OAK AND status=Closed', 'maxResults': '100',
               'expand': 'changelog',
               'fields': 'created'}
    
    response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
    data = json.loads(response.text)
    
    for elem in data['issues']:
        l_time = get_issue_item_to_time(elem, 'status', 'Closed')
        if l_time != []:
            close_list_dates.append(l_time[-1].date())

    close_list_dates.sort()
    close_list_dates.reverse()
    counter = Counter(close_list_dates)
    
    list_close_by_day = []
    
    
    for i in range(PERIOD, -1, -1):
        date = current_date - datetime.timedelta(days=i)
        k = counter[date]
        list_close_by_day.append(k)

    plt.plot(list_close_by_day, linewidth=3.0, color='green')
    plt.title(f'3. Графики открытых и закрытых задач за последние {PERIOD} дней')
    plt.xlabel('Дата')
    plt.ylabel('Количество задач')
    
    
    x_list = []
    for i in range(PERIOD+1):
        x_list.append(i)

    plt.xticks(x_list, labels=date_list, rotation=90, size=8)
    plt.show()

    summary_list_open = summ_elements(opened_issues_list)
    summary_list_close = summ_elements(list_close_by_day)

    plt.plot(summary_list_open, linewidth=3.0, color='grey')
    plt.plot(summary_list_close, linewidth=3.0, color='green')
    plt.title(f'3. Графики накопления открытых и закрытых задач за последние {PERIOD} дней')
    plt.xlabel('Дата')
    plt.ylabel('Количество задач')
    plt.xticks(x_list, labels=date_list, rotation=90, size=8)
    plt.show()
    # print(date_list)
    # print(dataset)
    # print(opened_issues_list)
#opened_and_closed_issues_per_day()

def user_tasks():
    payload = {'jql': 'project=KAFKA AND NOT assignee=null AND NOT reporter=null', 'maxResults': '1',
               'fields': 'reporter,assignee'}

    response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
    data = json.loads(response.text)
    total = int(data['total'])

    list_users = []

    for start_at in range(0, total, 1000):
        payload = {'jql': 'project=KAFKA AND NOT assignee=null AND NOT reporter=null', 'maxResults': '1000',
                   'startAt': f'{start_at}',
                   'fields': 'reporter,assignee'}

        response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
        data = json.loads(response.text)
        for elem in data['issues']:
            reporter = elem['fields']['reporter']['key']
            assignee = elem['fields']['assignee']['key']
            if reporter == assignee:
                list_users.append(reporter)

    list_users_30, list_numbers_30 = make_lists_name_num(list_users, 30)

    plt.plot(list_numbers_30, list_users_30, linewidth=3.0, color='green')
    plt.title(f'График пользователи и задачи')
    plt.ylabel('Пользователь')
    plt.xlabel('Количество задач')
    plt.show()

    plt.plot(list_numbers_30, linewidth=3.0, color='green')
    plt.title(f'График пользователи и задачи')
    plt.xlabel('Пользователь')
    plt.ylabel('Количество задач')
    x_list = []
    for i in range(30):
        x_list.append(i)
    plt.xticks(x_list, labels=list_users_30, rotation=45, size=8)
    plt.show()


def time_to_solve_the_problem(username):
    #username = 'nehanarkhede'
    list_5 = []
    payload = {'jql': 'project=KAFKA AND status=Closed AND NOT assignee=null', 'maxResults': '1000',
               'fields': 'assignee'}

    response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
    data = json.loads(response.text)
    for elem in data['issues']:
        assignee = elem['fields']['assignee']['key']
        list_5.append(assignee)

    counted_values = Counter(list_5)
    print(counted_values)

    ##################

    payload = {'jql': f'project=KAFKA AND status=Closed AND assignee={username}', 'maxResults': '1000',
               'expand': 'changelog',
               'fields': 'resolutiondate,created'}

    response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
    data = json.loads(response.text)

    times_list = []

    for elem in data['issues']:
        times_list.append(get_resolved_time_for_assignee(elem, username))

    plt.hist(times_list, bins=100, edgecolor='black', color='blue')

    plt.title(f'Гистограмма: пользователь {username}')
    plt.xlabel('Время решения (часы)')
    plt.ylabel('Количество задач')
    plt.tight_layout()
    plt.show()


def the_number_of_tasks_by_severity():
    list_x = ['Trivial', 'Minor', 'Major', 'Critical', 'Blocker']
    list_y = []
    for prio in list_x:
        payload = {'jql': f'project=KAFKA AND priority = {prio}', 'maxResults': '1', 'fields': 'priority'}
        response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
        data = json.loads(response.text)
        list_y.append(int(data['total']))


    plt.plot(list_y, linewidth=3.0, color='green')
    plt.title(f'График количество задач по степени серьезности')
    plt.xlabel('Приоритет')
    plt.ylabel('Количество задач')
    x_list = [0, 1, 2, 3, 4]
    plt.grid(True)
    plt.yticks(list_y)
    plt.xticks(x_list, labels=list_x)
    plt.show()