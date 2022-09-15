import tkinter as tk
from dataManage import playersName


playerList = list(playersName.keys())

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.list1 = []

        self.title('Player Input Window')
        self.geometry('450x400')

        self.label = tk.Label(self, text='Enter {} player name:'.format((len(self.list1)+1)), fg='Black', font='None 14')
        self.label.pack(pady= 10)

        self.entry = tk.Entry(self, font='None 20', width=20)
        self.entry.pack(pady=5)

        self.button = tk.Button(self, text="Submit", command = self.getPlayer)
        self.button.pack(pady=10)

        self.listbox = tk.Listbox(self)
        self.listbox.pack()

        self.listbox.bind('<Button-1>', self.fillout)

        self.entry.bind('<KeyRelease>', self.check)

        self.button2 = tk.Button(self, text="End", command=self.endWindow)
        self.button2.pack(padx = 10, pady=10)

        self.bind('<Return>', lambda event=None: self.button.invoke())

    
    def getPlayer(self):
        nm = self.entry.get()
        print(nm)
        if nm in playerList:
            name = playersName[nm]
            if name in self.list1:
                print('Player already in the team. Choose new player\n')
            else:
                self.list1.append(name)
                print("Player added successfully\n")
        else:
            print('Your given input is invalid\n')
        self.entry.delete(0, tk.END)
        self.label.configure(text='Enter {} player name:'.format((len(self.list1)+1)))
        self.update(playerList)
        if len(self.list1) > 10:
            self.destroy()

    
    def endWindow(self):
        self.list1.clear()
        self.destroy()


    def update(self, data):
        self.listbox.delete(0, tk.END)
        for item in data:
            self.listbox.insert(tk.END, item)


    def fillout(self, e):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.listbox.get(tk.ACTIVE))


    def check(self, e):
        temp = self.entry.get()
        if temp == '':
            data = playerList
        else:
            data = []
            for item in playerList:
                if temp.lower() in item.lower():
                    data.append(item)
        if data:
            self.button['state'] = 'normal'
        else:
            self.button['state'] = 'disabled'
        self.update(data)



def main():
    root = App()
    root.update(playerList)
    root.mainloop()
    return root.list1

if __name__ == '__main__':
    main()

