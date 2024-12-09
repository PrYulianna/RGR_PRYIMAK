import psycopg2
import random


class Model:
    def __init__(self):
        # Встановлення з'єднання з базою даних
        self.conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='1234',
            host='localhost',
            port=5432
        )

    def get_all_tables(self):
        c = self.conn.cursor()
        # Запит для отримання всіх таблиць з публічної схеми
        c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        return c.fetchall()

    def get_all_columns(self, table_name):
        c = self.conn.cursor()
        # Запит для отримання всіх колонок конкретної таблиці
        c.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,))
        return c.fetchall()

    def add_data(self, table_name, columns, val):
        c = self.conn.cursor()
        # Формування запиту для вставки даних у таблицю
        columns_str = ', '.join(f'"{col}"' for col in columns)
        placeholders = ', '.join(['%s'] * len(val))

        # Перевірка наявності ідентифікаторів в таблиці
        if table_name == 'Students-subjects':
            id_column = 'ID_connected'
        else:
            id_column = 'ID'

        c.execute(f'SELECT "{id_column}" FROM "{table_name}"')
        existing_identifiers = c.fetchall()
        existing_identifiers = [item for sublist in existing_identifiers for item in sublist]

        identifier_index = columns.index(id_column)
        val[identifier_index] = int(val[identifier_index])

        if val[identifier_index] in existing_identifiers:
            return 2  # Ідентифікатор вже існує

        # Перевірка на правильність зв'язків між студентами та предметами
        if table_name == 'Students-subjects':
            c.execute('SELECT "ID" FROM "Students"')
            student_ids = [item[0] for item in c.fetchall()]
            student_id_index = columns.index('StudentsID')
            if int(val[student_id_index]) not in student_ids:
                return 3  # Студент не знайдений

            c.execute('SELECT "ID" FROM "Subjects"')
            subject_ids = [item[0] for item in c.fetchall()]
            subject_id_index = columns.index('SubjectsID')
            if int(val[subject_id_index]) not in subject_ids:
                return 3  # Предмет не знайдений

        elif table_name == 'Grades':
            c.execute('SELECT "ID_connected" FROM "Students-subjects"')
            ss_ids = [item[0] for item in c.fetchall()]
            ss_id_index = columns.index('ConnectedID')
            if int(val[ss_id_index]) not in ss_ids:
                return 3  # Невірний зв'язок між студентами та предметами

        c.execute(f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})', val)
        self.conn.commit()
        return 1  # Дані успішно додано

    def edit_data(self, table_name, column, id, new_value):
        c = self.conn.cursor()

        # Перевірка наявності ідентифікаторів у таблиці
        if table_name == 'Students-subjects':
            id_column = 'ID_connected'
        else:
            id_column = 'ID'

        if column == id_column:
            c.execute(f'SELECT "{id_column}" FROM "{table_name}"')
            existing_identifiers = c.fetchall()
            existing_identifiers = [item for sublist in existing_identifiers for item in sublist]
            val_id = int(new_value)
            if val_id in existing_identifiers:
                return 2  # Ідентифікатор вже існує

        # Перевірка на правильність змін
        elif column in ['StudentsID', 'SubjectsID', 'ConnectedID']:
            referenced_table = {
                'StudentsID': 'Students',
                'SubjectsID': 'Subjects',
                'ConnectedID': 'Students-subjects'
            }[column]

            ref_id_column = 'ID_connected' if referenced_table == 'Students-subjects' else 'ID'
            c.execute(f'SELECT "{ref_id_column}" FROM "{referenced_table}"')
            referenced_values = [item[0] for item in c.fetchall()]
            val_id = int(new_value)
            if val_id not in referenced_values:
                return 3  # Некоректний ідентифікатор для зв'язку

        c.execute(f'UPDATE "{table_name}" SET "{column}" = %s WHERE "{id_column}" = %s', (new_value, id))
        self.conn.commit()
        return 1  # Дані успішно оновлені

    def delete_data(self, table_name, id):
        c = self.conn.cursor()

        try:
            self.conn.autocommit = False

            # Видалення даних зі зв'язками
            if table_name == 'Students':
                c.execute('SELECT "ID_connected" FROM "Students-subjects" WHERE "StudentsID" = %s', (id,))
                ss_ids = [row[0] for row in c.fetchall()]

                for ss_id in ss_ids:
                    c.execute('DELETE FROM "Grades" WHERE "ConnectedID" = %s', (ss_id,))

                c.execute('DELETE FROM "Students-subjects" WHERE "StudentsID" = %s', (id,))
                c.execute('DELETE FROM "Students" WHERE "ID" = %s', (id,))

            elif table_name == 'Subjects':
                c.execute('SELECT "ID_connected" FROM "Students-subjects" WHERE "SubjectsID" = %s', (id,))
                ss_ids = [row[0] for row in c.fetchall()]

                for ss_id in ss_ids:
                    c.execute('DELETE FROM "Grades" WHERE "ConnectedID" = %s', (ss_id,))

                c.execute('DELETE FROM "Students-subjects" WHERE "SubjectsID" = %s', (id,))
                c.execute('DELETE FROM "Subjects" WHERE "ID" = %s', (id,))

            elif table_name == 'Students-subjects':
                c.execute('DELETE FROM "Grades" WHERE "ConnectedID" = %s', (id,))
                c.execute('DELETE FROM "Students-subjects" WHERE "ID_connected" = %s', (id,))

            elif table_name == 'Grades':
                c.execute('DELETE FROM "Grades" WHERE "ID" = %s', (id,))

            self.conn.commit()
            return 1  # Дані успішно видалено

        except Exception as e:
            self.conn.rollback()
            print(f"Error during deletion: {e}")
            return 0
        finally:
            self.conn.autocommit = True

    def generate_data(self, table_name, count):
        c = self.conn.cursor()
        c.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s", (table_name,))
        columns_info = c.fetchall()

        # Генерація випадкових даних для таблиці
        for i in range(count):
            columns = []
            values = []

            if table_name == 'Students-subjects':
                c.execute('SELECT "ID" FROM "Students" ORDER BY RANDOM() LIMIT 1')
                student_id = c.fetchone()
                if not student_id:
                    print(f"Error: No students available for row {i + 1}")
                    continue

                c.execute('SELECT "ID" FROM "Subjects" ORDER BY RANDOM() LIMIT 1')
                subject_id = c.fetchone()
                if not subject_id:
                    print(f"Error: No subjects available for row {i + 1}")
                    continue

            elif table_name == 'Grades':
                c.execute('SELECT "ID_connected" FROM "Students-subjects" ORDER BY RANDOM() LIMIT 1')
                connected_id = c.fetchone()
                if not connected_id:
                    print(f"Error: No connected IDs available for row {i + 1}")
                    continue

            for column_info in columns_info:
                column_name = column_info[0]
                column_type = column_info[1]

                columns.append(f'"{column_name}"')

                if column_name == 'ID_connected' and table_name == 'Students-subjects':
                    c.execute('SELECT COALESCE(MAX("ID_connected"), 0) FROM "Students-subjects"')
                    max_id = c.fetchone()[0]
                    values.append(str(max_id + 1))

                elif column_name == 'ID':
                    c.execute(f'SELECT COALESCE(MAX("ID"), 0) FROM "{table_name}"')
                    max_id = c.fetchone()[0]
                    values.append(str(max_id + 1))

                elif column_name == 'StudentsID':
                    values.append(str(student_id[0]))

                elif column_name == 'SubjectsID':
                    values.append(str(subject_id[0]))

                elif column_name == 'ConnectedID':
                    values.append(str(connected_id[0]))

                elif column_name == 'Value' and table_name == 'Grades':
                    values.append(str(random.randint(1, 100)))

                elif column_type == 'integer':
                    values.append(str(random.randint(1, 100)))

                elif column_type == 'character varying':
                    if column_name in ['Name', 'Surname', 'Patronymic']:
                        values.append(f"'Test{i}'")
                    else:
                        values.append(f"'Text_{i}'")

            if columns and values:
                insert_query = f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({", ".join(values)})'
                try:
                    c.execute(insert_query)
                    self.conn.commit()
                except psycopg2.Error as e:
                    print(f"Error inserting row {i + 1}: {e}")
                    self.conn.rollback()
                    continue

        print(f"Data generation for table {table_name} completed")
