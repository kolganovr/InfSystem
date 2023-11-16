import random
import time
import threading
from matplotlib import pyplot as plt
import numpy as np

la = 0.3
p = 0.119
c = {1:2, 2:3, 3:3, 4:4}

FAST_MULT = 2 # Ускорение работы программы

TIME_HANDLE = p / la / FAST_MULT # Время обработки одной задачи

# Класс заявки
class Task:
    def __init__(self, importance):
        self.importance = importance
        self.startTime = time.time()
    
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

    def isEmpty(self):
        return self.items == []

    def add(self, item):
        self.items.insert(0, item)

    def pop(self):
        return self.items.pop()

    @property
    def size(self):
        return len(self.items)

    def getItem(self):
        # В зависимости от типа очереди (LIFO, FIFO, random) отправляем нужный элемент
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
            max = self.items[0]
            self.items = [max if item > max else item for item in self.items]
            self.items.remove(max)
            self.timeInQueue += time.time() - max.startTime
            return max
        
    def getQueue(self):
        return self.items
    
    def getTimeInQueue(self):
        # Получаем время в очереди для каждой задачи оставшейся в очереди
        for item in self.items:
            self.timeInQueue += time.time() - item.startTime
        return self.timeInQueue
        
    
# Класс Обработчика
class Handler:
    penalty = 0
    def __init__(self, queue):
        self.queue = queue
    
    def startWork(self):
        if queue.size == 1:
            # Если в очереди только одна задача, то обрабатываем ее сразу
            time.sleep(TIME_HANDLE)
            self.queue.getItem()
            return
        elif queue.size > 1:
            time.sleep(TIME_HANDLE)
            # Штрафуем за все задачи которые не выполняеются сейчас по правилу:
            # время выполнения * стоимость задачи
            items = self.queue.getQueue()
            for item in items:
                self.penalty += (time.time() - item.startTime) * c[item.importance] * FAST_MULT
        queue.getItem()

# Функции потоков
# Функция обработки задач
def handle_tasks():
    global task_count
    print(handler.queue.Qtype)
    while task_count > 0:
        if queue.size > 0:
            print(task_count, queue.size)
            handler.startWork()
            task_count -= 1

# Функция добавления задач
def add_tasks():
    global task_count
    while task_count > 0:
        if random.random() < p:
            importance = random.randint(1, 4)
            queue.add(Task(importance))
        time.sleep(0.025/FAST_MULT)

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
    # allTasks = []
    for timestamp in tasks:
        for k in range(4):
            importance[k].append(timestamp.count(k + 1))
        # allTasks.append(len(timestamp))
    # plt.plot(x, allTasks, label="allTasks")
    [plt.plot(x, importance[i], label=f"importance{i}") for i in range(4)]
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Tasks")
    plt.show()

if __name__ == "__main__":
    random.seed(1)
    task_count = 10
    tasks = []
    queue = Queue(4) # LIFO = 1, FIFO = 2, random = 3, priority = 4
    handler = Handler(queue)

    # Создаем два потока для обработки и добавления задач параллельно
    handle_thread = threading.Thread(target=handle_tasks)
    add_thread = threading.Thread(target=add_tasks)
    getTasks_thread = threading.Thread(target=getTasks)
    threads = [handle_thread, add_thread, getTasks_thread]


    # Запускаем потоки и ждем их окончания
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Выводим штраф
    print("Penalty: ", handler.penalty)
    print("Average time in queue: ", queue.getTimeInQueue() / (10 + queue.size) * FAST_MULT)

    # Строим графики
    graph(tasks)
