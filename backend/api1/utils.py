import random


def random_token(size=16, OnlyDigit=False):
    if OnlyDigit:
        alphavit = "1234567890"
        res = ""
        for i in range(1, size + 1):
            res += alphavit[random.randint() % len(alphavit)]
        return res
    else:
        alphavit = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOQRSTUVWXYZ"
        res = ""
        for i in range(1, size + 1):
            res += alphavit[random.randint(0, len(alphavit))]
        return res
