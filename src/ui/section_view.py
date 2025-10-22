from tkinter import Frame, Label, Entry, Button, Listbox, Scrollbar, StringVar, Toplevel, END, messagebox
from models.section import Section

class SectionView:
    def __init__(self, master, section: Section, on_update):
        self.master = master
        self.section = section
        self.on_update = on_update

        self.row_var = StringVar()
        self.seat_var = StringVar()
        self.selected_seats = []

        self.build_ui()

    def build_ui(self):
        frame = Frame(self.master)
        frame.pack()

        Label(frame, text=f"Section: {self.section.name}").grid(row=0, columnspan=4)

        Label(frame, text="Row:").grid(row=1, column=0)
        Entry(frame, textvariable=self.row_var).grid(row=1, column=1)

        Label(frame, text="Seat:").grid(row=1, column=2)
        Entry(frame, textvariable=self.seat_var).grid(row=1, column=3)

        Button(frame, text="Add Seat", command=self.add_seat).grid(row=2, column=0)
        Button(frame, text="Delete Seat", command=self.delete_seat).grid(row=2, column=1)
        Button(frame, text="Delete Row", command=self.delete_row).grid(row=2, column=2)
        Button(frame, text="Rename Section", command=self.rename_section).grid(row=2, column=3)

        self.seat_list = Listbox(frame, selectmode='multiple', width=50)
        self.seat_list.grid(row=3, columnspan=4)

        self.update_seat_list()

    def add_seat(self):
        row = self.row_var.get().strip().upper()
        seat = self.seat_var.get().strip().upper()
        if row and seat:
            self.section.add_seat(row, seat)
            self.update_seat_list()

    def delete_seat(self):
        selected_indices = self.seat_list.curselection()
        for index in selected_indices[::-1]:  # Delete from the end to avoid index shifting
            seat_info = self.seat_list.get(index).split()
            row = seat_info[0]
            seat = seat_info[1]
            self.section.delete_seat(row, seat)
        self.update_seat_list()

    def delete_row(self):
        row = self.row_var.get().strip().upper()
        if row:
            self.section.delete_row(row)
            self.update_seat_list()

    def rename_section(self):
        new_name = self.row_var.get().strip()
        if new_name:
            self.section.rename(new_name)
            self.on_update()  # Notify the main app to refresh the section list

    def update_seat_list(self):
        self.seat_list.delete(0, END)
        for seat in self.section.seats:
            self.seat_list.insert(END, f"{seat.row_number} {seat.seat_number}")