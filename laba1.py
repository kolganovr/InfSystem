import random
import time
import threading
from matplotlib import pyplot as plt
import numpy as np

la = 0.3
p = 0.119
c = {1:2, 2:3, 3:3, 4:4} # Важность задачи:штраф за единицу времени простоя 

FAST_MULT = 2 # Ускорение работы программы

TIME_HANDLE = p / la / FAST_MULT # Время обработки одной задачи

doNowTask = None 
interrupt = False

counter = 0

# Класс заявки
class Task:
    def __init__(self, importance):
        self.importance = importance
        self.startTime = time.time()
        self.timeHandled = 0
    
    def __str__(self):
        return "Importance " + str(self.importance) + ", time: " + str(self.startTime)
    
    # Сравнение важности заявок
    def __gt__(self, other):
        return self.importance > other.importance or (self.importance == other.importance and self.startTime < other.startTime)


# Класс очереди
class Queue:
    def __init__(self, Qtype):
        self.items = []
        self.timeInQueue = 0
        if Qtype == 1:
            self.Qtype = "LIFO"
        elif Qtype == 2:
            self.Qtype = "FIFO"
        elif Qtype == 3:
            self.Qtype = "random"
        elif Qtype == 4:
            self.Qtype = "priority"
        elif Qtype == 5:
            self.Qtype = "Abs priority"
        else:
            self.Qtype = "LIFO"

    def add(self, item):
        self.items.insert(0, item)

    def pop(self):
        return self.items.pop()

    def getItem(self):
        # В зависимости от типа очереди отправляем нужный элемент
        if self.Qtype == "LIFO":
            item = self.items.pop()
            self.timeInQueue += time.time() - item.startTime
            return item
        elif self.Qtype == "FIFO":
            elem = self.items[0]
            self.timeInQueue += time.time() - elem.startTime
            self.items.remove(elem)
            return elem
        elif self.Qtype == "random":
            elem = self.items[random.randint(0, self.size - 1)]
            self.timeInQueue += time.time() - elem.startTime
            self.items.remove(elem)
            return elem
        elif self.Qtype == "priority" or self.Qtype == "Abs priority":
            elem = self.items[0]
            for item in self.items:
                if item > elem:
                    elem = item
            self.timeInQueue += time.time() - elem.startTime
            self.items.remove(elem)
            return elem
        
    def getQueue(self):
        return self.items
        
# Класс Обработчика
class Handler:
    penalty = 0
    TimeByPriority = {1:0, 2:0, 3:0, 4:0}
    currentTask = None
    
    def startWork(self):
        global interrupt
        global doNowTask
        global counter
    
        self.currentTask = queue.getItem()
        counter += 1
        print("Start work with ", counter, " task", "priority: ", self.currentTask.importance)

        loopStartTime = time.time()
        while time.time() - loopStartTime + self.currentTask.timeHandled < TIME_HANDLE:     
            if interrupt and queue.Qtype == "Abs priority":
                loopStartTime = time.time()
                self.currentTask = doNowTask
                interrupt = False
                doNowTask = None

        # Штрафуем за все задачи которые не выполняеются сейчас по правилу:
        # время выполнения * стоимость задачи
        items = queue.getQueue()
        for item in items:
            self.penalty += (time.time() - item.startTime) * c[item.importance] * FAST_MULT
            self.TimeByPriority[item.importance] += (time.time() - item.startTime) * FAST_MULT
        
        self.currentTask = None

    def getTimeByPriority(self):
        items = queue.getQueue()
        for item in items:
            self.TimeByPriority[item.importance] += (time.time() - item.startTime) * FAST_MULT
        return self.TimeByPriority
        

# Функции потоков
# Функция обработки задач
def handle_tasks():
    global task_count
    print(queue.Qtype)
    while task_count > 0:
        if queue.size > 0:
            print(task_count, queue.size)
            handler.startWork()
            task_count -= 1

# Функция добавления задач
def add_tasks():
    global task_count
    global interrupt
    global doNowTask
    while task_count > 0:
        if random.random() < p:
            importance = random.randint(1, 4)
            if queue.Qtype == "Abs priority" and handler.currentTask and importance > handler.currentTask.importance:
                try:
                    print("Interrupt")
                    interrupt = True
                    handler.currentTask.timeHandled += time.time() - handler.currentTask.startTime
                    queue.add(handler.currentTask)
                    doNowTask = Task(importance)
                except:
                    print("Interrupt cancelled")
                    interrupt = False
                    doNowTask = None
                finally:
                    print("finally")
            else:
                queue.add(Task(importance))
        time.sleep(0.0001/FAST_MULT)

# Поточная функция считывания задач из очереди с их приоритетами и записью в список для дальнейшего вывода на график
def getTasks():
    global task_count
    while task_count > 0:
        temp = []
        for item in queue.getQueue():
            temp.append(item.importance)
        tasks.append(temp)
        time.sleep(0.025/FAST_MULT/10)

# Построения 4 графиков: кол-во задач каждого приоритета и общее кол-во задач от времени
def graph(tasks):
    importance = [[], [], [], []]
    x = np.arange(0, len(tasks), 1)
    for timestamp in tasks:
        for k in range(4):
            importance[k].append(timestamp.count(k + 1))
    [plt.plot(x, importance[i], label=f"importance{i}") for i in range(4)]
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Tasks")
    plt.show()

if __name__ == "__main__":
    random.seed(1)
    task_count = 20
    tasks = []
    queue = Queue(4) # LIFO = 1, FIFO = 2, random = 3, priority = 4, Abs priority = 5

    handler = Handler()

    # Создаем потоки
    handle_thread = threading.Thread(target=handle_tasks)
    add_thread = threading.Thread(target=add_tasks)
    getTasks_thread = threading.Thread(target=getTasks)
    threads = [handle_thread, add_thread, getTasks_thread]

    # Запускаем потоки
    for thread in threads:
        thread.start()

    # Ожидаем завершения потоков
    for thread in threads:
        thread.join()

    # Выводим информацию
    print()
    print(f'Queue type: {queue.Qtype}')
    print("Penalty: ", handler.penalty)
    TimeByPriority = handler.getTimeByPriority()
    print("Average time by priority: ", sum(TimeByPriority) / len(TimeByPriority))
    print(TimeByPriority)

    # Строим графики
    graph(tasks)
