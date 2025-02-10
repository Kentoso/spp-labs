from Pyro4 import expose
import random

class Solver(object):
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print "Inited"

    def solve(self):
        print "Job Started"
        num_workers = len(self.workers)
        print "Workers %d" % num_workers

        total_samples = self.read_input()

        a = 0.0
        b = 1.0
        samples_per_worker = total_samples / num_workers

        mapped = []
        for i in xrange(num_workers):
            mapped.append(self.workers[i].mymap(a, b, samples_per_worker))

        print "Map finished: ", mapped

        reduced = self.myreduce(mapped, a, b, total_samples)
        print "Reduce finished: " + str(reduced * 4)

        self.write_output(reduced * 4)
        print "Job Finished"

    @staticmethod
    @expose
    def mymap(a, b, samples):
        total = 0.0
        for _ in xrange(samples):
            x = a + (b - a) * random.random()
            total += (1 - x**2)**0.5

        return total

    @staticmethod
    @expose
    def myreduce(mapped, a, b, num_samples):
        total = 0.0
        for x in mapped:
            total += x.value
        integral = (b - a) * total / num_samples

        return integral

    def read_input(self):
        f = open(self.input_file_name, 'r')
        line = f.readline()
        f.close()
        return int(line.strip())

    def write_output(self, output):
        f = open(self.output_file_name, 'w')
        f.write(str(output) + "\n")
        f.close()
