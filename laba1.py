import random
import time
import threading

la = 0.3
p = 0.119
c = {1:2, 2:3, 3:3, 4:4}

TIME_HANDLE = p / la

# Класс заявки
class Task:
    def __init__(self, importance):
        self.importance = importance
        self.startTime = time.time()
    
    def __str__(self):
        return "Importance " + str(self.importance) + ", time: " + str(self.startTime)
    
    # Сравнение важности заявок
    def __gt__(self, other):
        return self.importance > other.importance or (self.importance == other.importance and self.startTime < other.time)


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
        
    def getQueue(self):
        return self.items
    
# Класс Обработчика
class Handler:
    penalty = 0
    def __init__(self, queue):
        self.queue = queue
    
    def startWork(self):
        time.sleep(TIME_HANDLE)
        if queue.size() > 1:
            # Штрафуем за все задачи которые не выполняеются сейчас по правилу:
            # время выполнения * стоимость задачи
            items = self.queue.getQueue()
            for i in items:
                self.penalty += (time.time() - i.startTime) * c[i.importance]
        queue.getItem()
    



def handle_tasks():
    global task_count
    while task_count > 0:
        if queue.size() > 0:
            print(task_count, queue.size())
            handler.startWork()
            task_count -= 1


def add_tasks():
    global task_count
    while task_count > 0:
        if random.random() < p:
            importance = random.randint(1, 4)
            queue.add(Task(importance))
        time.sleep(0.025)


if __name__ == "__main__":
    task_count = 10
    queue = Queue("FIFO")   # LIFO, FIFO, random
    handler = Handler(queue)

    # Создаем два потока
    handle_thread = threading.Thread(target=handle_tasks)
    add_thread = threading.Thread(target=add_tasks)

    # Запускаем потоки
    handle_thread.start()
    add_thread.start()

    # Ждем завершения потоков
    handle_thread.join()
    add_thread.join()

    print("Штраф: " + str(handler.penalty))
