import sys
from DBmodel import Model
from DBview import View

class Controller:
    def __init__(self):
        self.view = View()
        try:
            self.model = Model()
            self.view.show_message("Connected to the database")
        except Exception as e:
            self.view.show_message(f"An error occurred during initialization: {e}")
            sys.exit(1)

    def run(self):
        while True:
            choice = self.view.show_menu()
            if choice == '1':
                self.view_tables()
            elif choice == '2':
                self.view_columns()
            elif choice == '3':
                self.add_data()
            elif choice == '4':
                self.edit_data()
            elif choice == '5':
                self.delete_data()
            elif choice == '6':
                self.generate_data()
            elif choice == '7':
                break

    def view_tables(self):
        tables = self.model.get_all_tables()
        self.view.show_tables(tables)

    def view_columns(self):
        table_name = self.view.ask_table()
        columns = self.model.get_all_columns(table_name)
        self.view.show_columns(columns)

    def add_data(self):
        while True:
            table, columns, val = self.view.insert()
            error = self.model.add_data(table, columns, val)
            if int(error) == 1:
                self.view.show_message("Data added successfully!")
                break
            elif int(error) == 2:
                self.view.show_message("Unique identifier already exists!")
                break
            else:
                self.view.show_message("Invalid foreign key")
                break

    def edit_data(self):
        while True:
            table, column, id, new_value = self.view.update()
            error = self.model.edit_data(table, column, id, new_value)
            if int(error) == 1:
                self.view.show_message("Data updated successfully!")
                break
            elif int(error) == 2:
                self.view.show_message(f"Unique identifier {new_value} already exists!")
                break
            else:
                self.view.show_message(f"Invalid foreign key {new_value} in column {column}")
                break

    def delete_data(self):
        while True:
            table, id = self.view.delete()
            error = self.model.delete_data(table, id)
            if int(error) == 1:
                self.view.show_message("Row deleted successfully!")
                break
            else:
                self.view.show_message("Cannot delete the row, as there are related data")
                break

    def generate_data(self):
        table_name, num_rows = self.view.generate_data_input()
        self.model.generate_data(table_name, num_rows)
        self.view.show_message(f"Data for the {table_name} table was generated successfully")