import tkinter
from tkinter import ttk
from pathlib import Path
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
from modules.pyBjson import convertBjsonToJson
import json
import threading
from functools import partial
import sys, os, argparse
from modules.pyBjson.utils import uint_to_bytes, int_to_bytes, float_to_bytes

VERSION = "v1.0.2-dev"

def getBjsonContent(fp: str|Path):
    try:
        data = convertBjsonToJson(fp)
    except Exception as e:
        tkinter.messagebox.showerror("Unable to load file", f"Could not open the specified file. Error: {e}")
    return data

def addDictToTree(tree: ttk.Treeview, root: str, key: str, data: dict, count: int):
    if root == "":
        opened = True
    else:
        opened = False
    item_idx = count
    sub_node = tree.insert(root, "end", text=key, open=opened, values=["Object", item_idx])
    count += 1
    for key in data:
        if type(data[key]) == dict:
            count = addDictToTree(tree, sub_node, key, data[key], count)
        elif type(data[key]) == list:
            count = addListToTree(tree, sub_node, key, data[key], count)
        else:
            addSingleElementToTree(tree, sub_node, key, data[key], count)
            count += 1
    
    return count

def addListToTree(tree: ttk.Treeview, root: str, key: str, data: list, count: int):
    if root == "":
        opened = True
    else:
        opened = False
    item_idx = count
    sub_node = tree.insert(root, "end", text=key, open=opened, values=["Array", item_idx])
    count += 1
    for element in data:
        if type(element) == dict:
            count = addDictToTree(tree, sub_node, "Object", element, count)
        elif type(element) == list:
            count = addListToTree(tree, sub_node, "Array", element, count)
        elif type(element) == int or type(element) == float:
            addSingleElementToTree(tree, sub_node, "Number", element, count)
            count += 1
        elif type(element) == str:
            addSingleElementToTree(tree, sub_node, "String", element, count)
            count += 1
        elif type(element) == bool:
            addSingleElementToTree(tree, sub_node, "Boolean", element, count)
            count += 1
        else:
            addSingleElementToTree(tree, sub_node, "null", None, count)
            count += 1
        
    return count

def addSingleElementToTree(tree: ttk.Treeview, root: str, key: str, data, count: int):
    item_idx = count
    if type(data) == int or type(data) == float:
        tree.insert(root, "end", text=key, values=["Number", item_idx, data])
    elif type(data) == str:
        tree.insert(root, "end", text=key, values=["String", item_idx, data])
    elif type(data) == bool:
        tree.insert(root, "end", text=key, values=["Boolean", item_idx, data])
    else:
        tree.insert(root, "end", text=key, values=["null", item_idx, "null"])
    
def populate_tree(tree: ttk.Treeview, data: dict|list):
    count = 0
    if type(data) == dict:
        count = addDictToTree(tree, "", "root", data, count)
    elif type(data) == list:
        count = addListToTree(tree, "", "root", data, count)

def loadFileDataFromBjson(root, tree: ttk.Treeview, fp: str|Path):
    loading_label = tkinter.Label(root, text="Loading file...")
    loading_label.grid(row=0, column=0)
    try:
        json_str = getBjsonContent(fp)
        if json_str == None:
            tkinter.messagebox.showerror("Unable to load file", "The file could not be loaded. The format may be incorrect or unsupported.")
            loading_label.grid_remove()
            return
        bjson_dict = json.loads(json_str)

        populate_tree(tree, bjson_dict)
        if not hasattr(tree, 'icons'):
            tree.icons = {}
            tree.icons["objectLogo"] = tkinter.PhotoImage(file=os.path.join(root.app_path, "assets/object.png"))
            tree.icons["arrayLogo"] = tkinter.PhotoImage(file=os.path.join(root.app_path, "assets/array.png"))
            tree.icons["textLogo"] = tkinter.PhotoImage(file=os.path.join(root.app_path, "assets/text.png"))
            tree.icons["numberLogo"] = tkinter.PhotoImage(file=os.path.join(root.app_path, "assets/number.png"))
            tree.icons["booleanLogo"] = tkinter.PhotoImage(file=os.path.join(root.app_path, "assets/boolean.png"))
            tree.icons["nullLogo"] = tkinter.PhotoImage(file=os.path.join(root.app_path, "assets/null.png"))
        setIcons(tree, tree.icons)
        tree.grid(row=0, column=0, sticky="wesn")
        inputPath = Path(fp)
        root.title(f"MC3DS BJSON Editor - {inputPath.name}")
    except:
        pass

    loading_label.grid_remove()

def setIcons(tree: ttk.Treeview, icons: dict, parent=""):
    children = tree.get_children(parent)
    for child in children:
        item = tree.item(child)
        values = item["values"]
        if values[0] == "Object":
            tree.item(child, image=icons["objectLogo"])
        elif values[0] == "Array":
            tree.item(child, image=icons["arrayLogo"])
        elif values[0] == "String":
            tree.item(child, image=icons["textLogo"])
        elif values[0] == "Number":
            tree.item(child, image=icons["numberLogo"])
        elif values[0] == "Boolean":
            tree.item(child, image=icons["booleanLogo"])
        elif values[0] == "null":
            tree.item(child, image=icons["nullLogo"])
        else:
            print(f"Not match: {values[0]}")
        setIcons(tree, icons, child)

class App(tkinter.Tk):
    def __init__(self, fp = None):
        super().__init__()

        self.title("MC3DS BJSON Editor")
        self.geometry('640x400')
        self.columnconfigure(0, weight=4)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        if getattr(sys, 'frozen', False):
            self.running = "exe"
            self.app_path = sys._MEIPASS
            self.runningDir = os.path.dirname(sys.executable)
        elif __file__:
            self.running = "src"
            self.app_path = os.path.dirname(__file__)
            self.runningDir = os.path.dirname(__file__)

        os_name = os.name
        if os_name == "nt":
            self.iconbitmap(default=os.path.join(self.app_path, "icon.ico"))
        elif os_name == "posix":
            self.wm_iconbitmap()
            self.iconphoto(False, tkinter.PhotoImage(os.path.join(self.app_path, "icon.ico")))
        
        # -------------------------------
        menubar = tkinter.Menu(self)
        self.config(menu=menubar)

        file_menu = tkinter.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open", command=self.openFile)
        file_menu.add_command(label="Save as", command=self.saveChanges)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.closeApp)

        menubar.add_cascade(label="File", menu=file_menu, underline=0)

        help_menu = tkinter.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self.showAbout)

        menubar.add_cascade(label="Help", menu=help_menu, underline=0)
        # -------------------------------

        self.propertiesFrame = tkinter.Frame(self)
        self.propertiesFrame.grid(row=0, column=2, sticky="wnes")
        self.propertiesFrame.columnconfigure(1, weight=1)

        self.titlePropertiesLabel = tkinter.Label(self.propertiesFrame, text="Properties")
        self.titlePropertiesLabel.grid(row=0, column=0, sticky="we", columnspan=2)

        self.dataTypeLabel = tkinter.Label(self.propertiesFrame, text="Data type:")
        self.dataTypeLabel.grid(row=1, column=0, sticky="e", padx=(5, 0))

        self.dataTypeStringVar = tkinter.StringVar(value="")
        self.dataTypeEntry = tkinter.ttk.Entry(self.propertiesFrame, textvariable=self.dataTypeStringVar, state="readonly")
        self.dataTypeEntry.grid(row=1, column=1, sticky="we", padx=5, pady=5)

        self.valueLabel = tkinter.Label(self.propertiesFrame, text="Value:")
        self.valueLabel.grid(row=2, column=0, sticky="e", padx=(5, 0))

        self.valueStringVar = tkinter.StringVar(value="")
        self.valueEntry = tkinter.ttk.Entry(self.propertiesFrame, textvariable=self.valueStringVar, state="readonly")
        self.valueEntry.grid(row=2, column=1, sticky="we", padx=5, pady=5)

        self.saveButton = tkinter.ttk.Button(self.propertiesFrame, state="disabled", text="Ok", command=self.registerChange)
        self.saveButton.grid(row=3, column=0, columnspan=2)

        self.tree = ttk.Treeview(self, show='tree', selectmode="browse")
        self.tree.bind('<<TreeviewSelect>>', self.itemSelected)
        self.scrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.lastValue = None
        self.filePath = fp
        self.changes = []
        self.actualIndex = None

        if fp != None:
            threading.Thread(target=partial(loadFileDataFromBjson, self, self.tree, fp)).start()

        self.saved = True

    def registerChange(self):
        index = self.actualIndex
        dataType = self.dataTypeStringVar.get()
        newValue = self.valueStringVar.get()
        if dataType == "Number":
            self.lastValue = float(self.lastValue)
            if int(self.lastValue) == self.lastValue:
                self.lastValue = int(self.lastValue)
            try:
                newValue = float(newValue)
                if int(newValue) == newValue:
                    newValue = int(newValue)
            except:
                pass
        if newValue != self.lastValue:
            if dataType == "Boolean":
                if newValue != "true" and newValue != "false":
                    tkinter.messagebox.showwarning(title="Invalid value", message="Boolean values only accept 'true' or 'false'")
                    return
            if (type(newValue) == type(self.lastValue)) or ((type(newValue) == int or type(newValue) == float) and dataType == "Number"):
                for element in self.changes:
                    if element[0] == index:
                        self.changes.remove(element)
                newItem = [index, dataType, newValue]
                self.changes.append(newItem)
                print("Change registered")
                self.saved = False
            else:
                tkinter.messagebox.showwarning(title="Invalid value", message="The value entered is not valid for this instance")

    def saveChanges(self):
        if type(self.filePath) == str:
            with open(self.filePath, "rb") as f:
                fileContent = list(f.read())
            for element in self.changes:
                idx = element[0] * 3 + 1
                if element[1] == "Number":
                    if type(element[2]) == int:
                        data_id = list(uint_to_bytes(2, "little"))
                        value = list(int_to_bytes(element[2], "little"))
                    else:
                        data_id = list(uint_to_bytes(3, "little"))
                        value = list(float_to_bytes(element[2], "little"))
                elif element[1] == "Boolean":
                    if element[2] == "true":
                        data_id = list(uint_to_bytes(1, "little"))
                        value = list(int_to_bytes(1, "little"))
                    else:
                        data_id = list(uint_to_bytes(1, "little"))
                        value = list(int_to_bytes(0, "little"))
                if element[1] == "Number" or element[1] == "Boolean":
                    fileContent[idx*4:idx*4+4] = data_id
                    fileContent[idx*4+4:idx*4+8] = value
            outputPath = tkinter.filedialog.asksaveasfilename(defaultextension=".bjson", filetypes=[("BJSON Files", ".bjson")])
            if outputPath != "":
                with open(outputPath, "wb") as f:
                    f.write(bytearray(fileContent))
                self.clearTreeview()
                self.tree.grid_remove()
                threading.Thread(target=partial(loadFileDataFromBjson, self, self.tree, outputPath)).start()
                self.valueEntry.configure(state="readonly")
                self.valueStringVar.set("")
                self.dataTypeStringVar.set("")
                self.lastValue = None
                self.changes = []
                self.actualIndex = None
                self.filePath = outputPath
                self.saved = True

    def openFile(self):
        if self.askForChanges():
            inputFp = tkinter.filedialog.askopenfilename(filetypes=[("BJSON Files", ".bjson")])
            if inputFp != "":
                self.clearTreeview()
                self.tree.grid_remove()
                threading.Thread(target=partial(loadFileDataFromBjson, self, self.tree, inputFp)).start()
                self.valueEntry.configure(state="readonly")
                self.valueStringVar.set("")
                self.dataTypeStringVar.set("")
                self.saveButton.configure(state="disabled")
                self.lastValue = None
                self.changes = []
                self.actualIndex = None
                self.filePath = inputFp
                self.saved = True

    def clearTreeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def itemSelected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            self.dataTypeStringVar.set(record[0])
            self.actualIndex = record[1]
            if len(record) > 2:
                for element in self.changes:
                    if element[0] == record[1]:
                        record[2] = element[2]
                if record[0] != "Boolean":
                    self.valueStringVar.set(record[2])
                    self.lastValue = record[2]
                else:
                    if record[2] == True:
                        self.valueStringVar.set("true")
                        self.lastValue = "true"
                    else:
                        self.valueStringVar.set("false")
                        self.lastValue = "false"
                if record[0] != "String" and record[0] != "null":
                    self.valueEntry.configure(state="normal")
                    self.saveButton.configure(state="normal")
                else:
                    self.valueEntry.configure(state="readonly")
                    self.saveButton.configure(state="disabled")
            else:
                self.valueStringVar.set("")
                self.valueEntry.configure(state="readonly")
                self.saveButton.configure(state="disabled")
            message = ""
            for element in record:
                message = f"{message}{element} "
            print(message)

    def closeApp(self, val=None):
        if self.saved:
            sys.exit()
        else:
            print("Not saved")
            op = tkinter.messagebox.askyesnocancel(title="Unsaved changes", message="There are unsaved changes. Would you like to save them before exit?")
            if op == True:
                self.saveChanges()
                sys.exit()
            elif op == False:
                sys.exit()
            else:
                pass
    
    def askForChanges(self):
        if self.saved:
            return True
        else:
            print("Not saved")
            op = tkinter.messagebox.askyesnocancel(title="Unsaved changes", message="There are unsaved changes. Would you like to save them?")
            if op == True:
                self.saveChanges()
                return True
            elif op == False:
                return True
            else:
                return False
            
    def showAbout(self):
        about_text = f"MC3DS BJSON Editor\nVersion {VERSION}\n\nMade by: STBrian\nGitHub: https://github.com/STBrian"
        tkinter.messagebox.showinfo("About", about_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A MC3DS BJSON Editor')
    parser.add_argument('path', nargs='?', type=str, help='File path to open')
    args = parser.parse_args()

    if args.path != None:
        if os.path.exists(args.path):
            app = App(args.path)
    else:
        app = App()

    app.bind('<Alt-F4>', app.closeApp)
    app.protocol("WM_DELETE_WINDOW", app.closeApp)

    app.mainloop()