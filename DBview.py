import time

class View:
    def show_menu(self):
        while True:
            print("Menu:")
            print("1. Tables output")
            print("2. Column names output")
            print("3. Add data")
            print("4. Update data")
            print("5. Delete data")
            print("6. Generate data")
            print("7. Exits")
            choice = input("Choose: ")
            if choice in ('1', '2', '3', '4', '5', '6', '7'):
                return choice
            else:
                print("Incorrect option, try again")
                time.sleep(2)

    def show_message(self, message):
        print(message)
        time.sleep(2)

    def show_tables(self, tables):
        print("Table names:")
        for table in tables:
            print(table)
        time.sleep(2)

    def ask_table(self):
        table_name = input("Enter Table name: ")
        return table_name

    def show_columns(self, columns):
        print("Column names:")
        for column in columns:
            print(column)
        time.sleep(2)

    def insert(self):
        while True:
            try:
                table = input("Enter table name: ")
                columns = input("[Use Spaces] Enter column names: ").split()
                val = input("[Use Spaces] Enter data: ").split()
                if len(columns) != len(val):
                    raise ValueError("Incorrect input.")
                return table, columns, val
            except ValueError as e:
                print(f"Error: {e}")

    def update(self):
        while True:
            try:
                table = input("Enter table name: ")
                column = input("Enter column name: ")
                id = int(input("Enter row ID: "))
                new_value = input("Enter new value: ")
                return table, column, id, new_value
            except ValueError as e:
                print(f"Error: {e}")

    def delete(self):
        while True:
            try:
                table = input("Enter table name: ")
                id = int(input("Enter row ID: "))
                return table, id
            except ValueError as e:
                print(f"Error: {e}")

    def generate_data_input(self):
        while True:
            try:
                table_name = input("Enter table name: ")
                num_rows = int(input("Enter number of rows to generate: "))
                return table_name, num_rows
            except ValueError as e:
                print(f"Errorа: {e}")