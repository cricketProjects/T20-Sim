from customSeries import main
import os


if __name__ == '__main__':
    print("\n\t-----WELCOME {} TO T20 SIMULATION-----\t\n".format(os.getlogin().upper()))
    a = True
    while(a == True):
        main()
        print()
        end1 = input('Type "q" to quit or any other key to continue.')
        a = ('q'.lower()== end1.lower())
    print()
