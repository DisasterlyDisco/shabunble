import time

def main():
    counter = 10
    while True:
        print("\x1b[2J\x1b[H")
        if counter > 0:
            if counter == 10:
                punctuation = '...'
            elif counter > 6:
                punctuation = '....'
            elif counter > 3:
                punctuation = '...!'
            elif counter == 3:
                punctuation = '..!!'
            elif counter == 2:
                punctuation = '.!!!'
            else :
                punctuation = '!!!!'

            print(f'{counter}{punctuation}')

            counter -= 1
            time.sleep(1)
        else:
            print('                               _.-^^---....,,--                                ')
            print('                           _--                  --_                            ')
            print('                          <                        >)                          ')
            print('                          |                         |                          ')
            print('                           \._                   _./                           ')
            print("                              ```--. . , ; .--'''                              ")
            print('                                    | |   |                                    ')
            print('                                 .-=||  | |=-.                                 ')
            print("                                 `-=#$%&%$#=-'                                 ")
            print("                                    | ;  :|                                    ")
            print("________________________________.,-#%&$@%#&#~,.________________________________")
            counter = 10
            time.sleep(9)
        

if __name__ == "__main__":
    main()