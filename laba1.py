import random
import time
import threading

la = 0.3
p = 0.119
c = {1:2, 2:3, 3:3, 4:4}

FAST_MULT = 1

TIME_HANDLE = p / la / FAST_MULT

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
        self.Qtype = Qtype

    def isEmpty(self):
        return self.items == []

    def add(self, item):
        self.items.insert(0, item)

    def pop(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

    def getItem(self):
        # В зависимости от типа очереди (LIFO, FIFO, random) отправляем нужный элемент
        if self.Qtype == "LIFO":
            return self.pop()
        elif self.Qtype == "FIFO":
            elem = self.items[0]
            self.items.remove(elem)
            return elem
        elif self.Qtype == "random":
            elem = self.items[random.randint(0, self.size()-1)]
            self.items.remove(elem)
            return elem
        elif self.Qtype == "priority":
            max = self.items[0]
            for item in self.items:
                if item > max:
                    max = item
            self.items.remove(max)
            return max
        
    def getQueue(self):
        return self.items
    
# Класс Обработчика
class Handler:
    penalty = 0
    def __init__(self, queue):
        self.queue = queue
    
    def startWork(self):
        if queue.size() == 1:
            # Если в очереди только одна задача, то обрабатываем ее сразу
            time.sleep(TIME_HANDLE)
            self.queue.getItem()
            return
        elif queue.size() > 1:
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
        if queue.size() > 0:
            print(task_count, queue.size())
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

if __name__ == "__main__":
    timeStart = time.time()
    # Seed для генератора случайных чисел
    random.seed(1)
    task_count = 10
    queue = Queue("LIFO") # LIFO, FIFO, random, priority
    handler = Handler(queue)

    # Создаем два потока для обработки и добавления задач параллельно
    handle_thread = threading.Thread(target=handle_tasks)
    add_thread = threading.Thread(target=add_tasks)

    # Запускаем потоки
    handle_thread.start()
    add_thread.start()

    # Ждем завершения потоков
    handle_thread.join()
    add_thread.join()

    print("Штраф: " + str(handler.penalty))
    print("Время работы: " + str(time.time() - timeStart))
