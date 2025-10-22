from tkinter import Tk, Frame, Label, Entry, Button, Listbox, Scrollbar, StringVar, Toplevel, END, messagebox
import json
from models.seating_plan import SeatingPlan
from ui.section_view import SectionView

class MainWindow:
    def __init__(self, root):
        self.plan = SeatingPlan()
        self.root = root
        self.root.title("Seating Plan Builder")

        self.section_name = StringVar()
        self.row = StringVar()
        self.seat = StringVar()

        self.build_main_ui()

    def build_main_ui(self):
        Frame(self.root).pack()

        Label(self.root, text="Section Name:").pack()
        Entry(self.root, textvariable=self.section_name).pack()
        Button(self.root, text="Create Section", command=self.create_section).pack()

        self.section_list = Listbox(self.root, width=40)
        self.section_list.pack()

        Button(self.root, text="View Section", command=self.view_section).pack()
        Button(self.root, text="Delete Section", command=self.delete_section).pack()
        Button(self.root, text="Export Plan", command=self.export_plan).pack()
        Button(self.root, text="Import Plan", command=self.import_plan).pack()

    def create_section(self):
        name = self.section_name.get().strip()
        if name:
            self.plan.add_section(name)
            if name not in self.section_list.get(0, END):
                self.section_list.insert(END, name)
            self.section_name.set("")

    def delete_section(self):
        sel = self.section_list.curselection()
        if sel:
            name = self.section_list.get(sel[0])
            self.plan.delete_section(name)
            self.section_list.delete(sel[0])

    def view_section(self):
        sel = self.section_list.curselection()
        if not sel:
            return
        section_name = self.section_list.get(sel[0])
        section_view = SectionView(self.root, self.plan, section_name)
        section_view.open()

    def export_plan(self):
        with open("seating_plan.json", "w") as f:
            json.dump(self.plan.to_dict(), f, indent=2)
        messagebox.showinfo("Export", "Plan exported to seating_plan.json")

    def import_plan(self):
        try:
            with open("seating_plan.json", "r") as f:
                data = json.load(f)
                self.plan.from_dict(data)
                self.section_list.delete(0, END)
                for name in self.plan.sections.keys():
                    self.section_list.insert(END, name)
            messagebox.showinfo("Import", "Plan imported successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))