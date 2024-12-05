import multiprocessing

def decomp(n):
    L = dict()
    k = 2
    while n != 1:
        exp = 0
        while n % k == 0:
            n = n // k
            exp += 1
        if exp != 0:
            L[k] = exp
        k = k + 1
        
    return L

def ppcm(a:int,b:int) -> dict:
    Da = decomp(a)
    Db = decomp(b)
    p = 1
    for facteur , exposant in Da.items():
        if facteur in Db:
            exp = max(exposant , Db[facteur])
        else:
            exp = exposant
        
        p *= facteur**exp
        
    for facteur , exposant in Db.items():
        if facteur not in Da:
            p *= facteur**exposant
            
    return p

class Event():
    def __init__(self):
        self.state = False
        self.count = 0
        self.transmit = 0

    def listen(self):
        self.count += 1

    def trigger(self):
        import time
        count = self.count
        self.state = True
        start = time.time()
        while count > 0 and (time.time()-start) < 2:
            while self.transmit != 0:
                self.transmit -= 1
                count -= 1
        self.state = False

    def get(self):
        self.transmit += 1
        return self.state

def split_lines(dictionary:dict):
    frame = list(dictionary.items())[0][1]
    lines = frame.split("\n")
    while True:
        try:
            lines.remove("")
        except ValueError:
            break
    number_of_lines = len(lines)
    print(number_of_lines)
    lines_dict = {}
    for frame_ in list(dictionary.items()):
        frame = frame_[1]
        lines = frame.split("\n")
        print(len(lines))
        for i in range(number_of_lines):
            print(i)
            lines_dict[i] = lines[i]
    
    return (number_of_lines,lines_dict)

class Process():
    def __init__(self,threads_number):
        pass

class Printer():

    def __init__(self,dictionary,number_of_lines,process):
        self.dictionary = dictionary
        self.nunumber_of_lines = number_of_lines
        self.process = process
        self.thread_dict = {}

        threads_per_process = number_of_lines // process
        rest = number_of_lines % process

        for handle in range(process):
            self.thread_dict[handle] = threads_per_process
        
        a = 0
        while rest != 0:
            self.thread_dict[a] += 1
            a += 0
            rest -= 1

    def print_lines(self,list,event:Event):
        for element in list:
            while not event.get():
                pass
            print(element)
    
    def assign_func(self,event,*args,**kwargs):
        import threading
        thread_dict = {}
        for index,arg in enumerate(args):
            thread_dict[index] = threading.Thread(target=self.print_lines,args = (arg,))


    def launch(self):
        event = Event()
        with multiprocessing.Pool(self.process) as pool:
            pool.map(self.assign_func,(event,))