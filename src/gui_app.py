from tkinter import Tk, Frame, Label, Entry, Button, Listbox, Scrollbar, StringVar, Toplevel, END, messagebox
import json
from seatingplan import SeatingPlan

class SeatingApp:
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
        Button(self.root, text="Clone Section", command=self.clone_section).pack()

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

    def clone_section(self):
        sel = self.section_list.curselection()
        if sel:
            name = self.section_list.get(sel[0])
            new_name = f"{name}_copy"
            self.plan.clone_section(name, new_name)
            self.section_list.insert(END, new_name)

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
        win = Toplevel(self.root)
        win.title(f"Section: {section_name}")

        Label(win, text="Row:").grid(row=0, column=0)
        Entry(win, textvariable=self.row).grid(row=0, column=1)
        Label(win, text="Seat:").grid(row=0, column=2)
        Entry(win, textvariable=self.seat).grid(row=0, column=3)
        Button(win, text="Add Seat", command=lambda: self.add_seat(section_name)).grid(row=0, column=4)
        Button(win, text="Add Seat Range", command=lambda: self.add_seat_range(section_name)).grid(row=1, column=4)

        Button(win, text="Delete Seat", command=lambda: self.delete_seat(section_name)).grid(row=2, column=4)
        Button(win, text="Delete Row", command=lambda: self.delete_row(section_name)).grid(row=3, column=4)

        self.grid_frame = Frame(win)
        self.grid_frame.grid(row=4, column=0, columnspan=5)
        self.update_grid(section_name)

    def add_seat(self, section_name):
        row = self.row.get().strip().upper()
        seat = self.seat.get().strip().upper()
        if row and seat:
            self.plan.sections[section_name].add_seat(row, seat)
            self.update_grid(section_name)

    def add_seat_range(self, section_name):
        row = self.row.get().strip().upper()
        start_seat = self.seat.get().strip().upper()
        end_seat = self.seat.get().strip().upper()
        if row and start_seat and end_seat:
            self.plan.sections[section_name].add_seat_range(row, start_seat, end_seat)
            self.update_grid(section_name)

    def delete_seat(self, section_name):
        row = self.row.get().strip().upper()
        seat = self.seat.get().strip().upper()
        if row and seat:
            self.plan.sections[section_name].delete_seat(row, seat)
            self.update_grid(section_name)

    def delete_row(self, section_name):
        row = self.row.get().strip().upper()
        if row:
            self.plan.sections[section_name].delete_row(row)
            self.update_grid(section_name)

    def update_grid(self, section_name):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        section = self.plan.sections[section_name]
        layout = {}
        for seat in section.seats:
            layout.setdefault(seat.row_number, []).append(seat.seat_number)
        for r_idx, row in enumerate(sorted(layout)):
            Label(self.grid_frame, text=row).grid(row=r_idx, column=0)
            for c_idx, seat in enumerate(sorted(layout[row])):
                Label(self.grid_frame, text=seat).grid(row=r_idx, column=c_idx + 1)

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

if __name__ == "__main__":
    root = Tk()
    app = SeatingApp(root)
    root.mainloop()