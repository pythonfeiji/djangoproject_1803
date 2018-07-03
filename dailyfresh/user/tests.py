from django.test import TestCase

# Create your tests here.

class A:
    @classmethod
    def f(self):
        print('A...f...')
        super().f()

class B:
    @classmethod
    def f(self):
        print('B...f...')


class C(A,B):
    @classmethod
    def get(self):
        super().f()


C.get()