

def maxims():
    from random import randint
    '''Reads the maxims and passes the variable to function
    according to input'''
    contentslist = []
    with open("maxims.txt", "r") as maximlist:
        maximlines = maximlist.readlines()
        maximlist.close()
        for i in maximlines:
            contentslist.append(i)

    maximselection = randint(0, len(contentslist))
    return "{}".format(contentslist[maximselection])
