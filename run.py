from lab_work.main import *


while 1:
    ask = input("Введите номер графика, который требуется отобразить"
                "\n1 - гистограмма, отражающая время, которое задача провела в открытом состоянии"
                "\n2 - диаграмма показывающая распределение времени по состояниям задач"
                "\n3 - график, показывающий количество заведенных и закрытых задач в день"
                "\n4 - график, выражающий общее количество задач пользователя"
                "\n5 - гистограмма, отражающая время, которое затратил пользователь на ее выполнение"
                "\n6 - график, выражающий количество задач по степени серьёзности"
                "\n0 - завершить выполнение программы\n"
                )

    if ask == "1":
        time_to_solve_the_issue()
    elif ask == "2":
        distribution_of_time_by_tasks()
    elif ask == "3":
        opened_and_closed_issues_per_day()
    elif ask == "4":
        user_tasks()
    elif ask == "5":
        time_to_solve_the_problem(input('Введите имя пользователя:\n'))
    elif ask == "6":
        the_number_of_tasks_by_severity()
    elif ask == "0":
        exit(0)
    else:
        print("Введён не корректный номер графика")
