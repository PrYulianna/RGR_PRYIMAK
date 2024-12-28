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
            try:
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
                    self.view.show_message("Exiting the application. Goodbye!")
                    break
                else:
                    self.view.show_message("Invalid choice. Please try again.")
            except Exception as e:
                self.view.show_message(f"An unexpected error occurred: {e}")

    def view_tables(self):
        try:
            tables = self.model.get_all_tables()
            if tables:
                self.view.show_tables(tables)
            else:
                self.view.show_message("No tables found in the database.")
        except Exception as e:
            self.view.show_message(f"Error fetching tables: {e}")

    def view_columns(self):
        try:
            table_name = self.view.ask_table()
            columns = self.model.get_all_columns(table_name)
            if columns:
                self.view.show_columns(columns)
            else:
                self.view.show_message(f"No columns found for table {table_name}.")
        except Exception as e:
            self.view.show_message(f"Error fetching columns: {e}")

    def add_data(self):
        while True:
            try:
                table, columns, val = self.view.insert()
                error = self.model.add_data(table, columns, val)
                self._handle_add_edit_response(error, "added")
                break
            except Exception as e:
                self.view.show_message(f"Error adding data: {e}")

    def edit_data(self):
        while True:
            try:
                table, column, id, new_value = self.view.update()
                error = self.model.edit_data(table, column, id, new_value)
                self._handle_add_edit_response(error, "updated")
                break
            except Exception as e:
                self.view.show_message(f"Error updating data: {e}")

    def delete_data(self):
        while True:
            try:
                table, id = self.view.delete()
                error = self.model.delete_data(table, id)
                if error == 1:
                    self.view.show_message("Row deleted successfully!")
                else:
                    self.view.show_message("Cannot delete the row, as there are related data.")
                break
            except Exception as e:
                self.view.show_message(f"Error deleting data: {e}")

    def generate_data(self):
        try:
            table_name, num_rows = self.view.generate_data_input()
            self.model.generate_data(table_name, num_rows)
            self.view.show_message(f"Data for the {table_name} table was generated successfully")
        except Exception as e:
            self.view.show_message(f"Error generating data: {e}")

    def _handle_add_edit_response(self, error, action):
        if error == 1:
            self.view.show_message(f"Data {action} successfully!")
        elif error == 2:
            self.view.show_message("Unique identifier already exists!")
        elif error == 3:
            self.view.show_message("Invalid foreign key or related data not found.")
        else:
            self.view.show_message("An unknown error occurred.")
