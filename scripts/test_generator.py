import string
import random

class TestGenerator:
    def __init__(self, flood_count):
        self.count = flood_count

    def string_generator(self):
        """
        Random string generator for custom size
        """
        N = 1000
        return ''.join(random.choice(string.ascii_uppercase +
                                     string.digits) for x in range(N))
    def file_generate(self):
        """ Generates self.count files in a <tests> folder"""
        files = []
        for i in range(1, self.count):
            filename = "tests/test_%s" % i
            with open(filename, "w") as fo:
                fo.write(self.string_generator())
            files.append(filename)

        return files


if __name__=="__main__":
    dbf = TestGenerator(10)
    dbf.file_generate()
