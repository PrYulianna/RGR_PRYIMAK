import time

class View:
    def show_menu(self):
        while True:
            print("\nMenu:")
            print("1. Tables output")
            print("2. Column names output")
            print("3. Add data")
            print("4. Update data")
            print("5. Delete data")
            print("6. Generate data")
            print("7. Exit")
            choice = input("Choose an option: ")
            if choice in ('1', '2', '3', '4', '5', '6', '7'):
                return choice
            else:
                self.show_message("Incorrect option, please try again.")

    def show_message(self, message):
        print(f"\n{message}")
        time.sleep(1)

    def show_tables(self, tables):
        print("\nTable names:")
        if tables:
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("No tables found.")
        time.sleep(1)

    def ask_table(self):
        return input("\nEnter the table name: ").strip()

    def show_columns(self, columns):
        print("\nColumn names:")
        if columns:
            for column in columns:
                print(f"- {column[0]}")
        else:
            print("No columns found.")
        time.sleep(1)

    def insert(self):
        while True:
            try:
                table = self.ask_table()
                columns = input("Enter column names (separated by spaces): ").strip().split()
                val = input("Enter values (separated by spaces): ").strip().split()

                if len(columns) != len(val):
                    raise ValueError("The number of columns and values must match.")

                return table, columns, val
            except ValueError as e:
                self.show_message(f"Error: {e}")

    def update(self):
        while True:
            try:
                table = self.ask_table()
                column = input("Enter the column name to update: ").strip()
                id = int(input("Enter the row ID: ").strip())
                new_value = input("Enter the new value: ").strip()
                return table, column, id, new_value
            except ValueError as e:
                self.show_message(f"Error: {e}")

    def delete(self):
        while True:
            try:
                table = self.ask_table()
                id = int(input("Enter the row ID to delete: ").strip())
                return table, id
            except ValueError as e:
                self.show_message(f"Error: {e}")

    def generate_data_input(self):
        while True:
            try:
                table_name = self.ask_table()
                num_rows = int(input("Enter the number of rows to generate: ").strip())
                return table_name, num_rows
            except ValueError as e:
                self.show_message(f"Error: {e}")
