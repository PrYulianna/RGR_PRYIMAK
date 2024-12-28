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
        with self.conn.cursor() as c:
            c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            return c.fetchall()

    def get_all_columns(self, table_name):
        with self.conn.cursor() as c:
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,))
            return c.fetchall()

    def add_data(self, table_name, columns, val):
        with self.conn.cursor() as c:
            columns_str = ', '.join(f'"{col}"' for col in columns)
            placeholders = ', '.join(['%s'] * len(val))

            id_column = 'ID_connected' if table_name == 'Students-subjects' else 'ID'

            c.execute(f'SELECT "{id_column}" FROM "{table_name}"')
            existing_identifiers = [row[0] for row in c.fetchall()]

            identifier_index = columns.index(id_column)
            val[identifier_index] = int(val[identifier_index])

            if val[identifier_index] in existing_identifiers:
                return 2  # Ідентифікатор вже існує

            if table_name == 'Students-subjects':
                if not self._validate_foreign_key(c, 'Students', 'ID', val[columns.index('StudentsID')]):
                    return 3  # Студент не знайдений

                if not self._validate_foreign_key(c, 'Subjects', 'ID', val[columns.index('SubjectsID')]):
                    return 3  # Предмет не знайдений

            elif table_name == 'Grades':
                if not self._validate_foreign_key(c, 'Students-subjects', 'ID_connected', val[columns.index('ConnectedID')]):
                    return 3  # Невірний зв'язок

            c.execute(f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})', val)
            self.conn.commit()
            return 1  # Дані успішно додано

    def edit_data(self, table_name, column, id, new_value):
        with self.conn.cursor() as c:
            id_column = 'ID_connected' if table_name == 'Students-subjects' else 'ID'

            if column == id_column:
                c.execute(f'SELECT "{id_column}" FROM "{table_name}"')
                if int(new_value) in [row[0] for row in c.fetchall()]:
                    return 2  # Ідентифікатор вже існує

            elif column in ['StudentsID', 'SubjectsID', 'ConnectedID']:
                referenced_table = {
                    'StudentsID': 'Students',
                    'SubjectsID': 'Subjects',
                    'ConnectedID': 'Students-subjects'
                }[column]

                ref_id_column = 'ID_connected' if referenced_table == 'Students-subjects' else 'ID'
                if not self._validate_foreign_key(c, referenced_table, ref_id_column, new_value):
                    return 3  # Некоректний зв'язок

            c.execute(f'UPDATE "{table_name}" SET "{column}" = %s WHERE "{id_column}" = %s', (new_value, id))
            self.conn.commit()
            return 1  # Дані успішно оновлені

    def delete_data(self, table_name, id):
        with self.conn.cursor() as c:
            try:
                self.conn.autocommit = False

                if table_name == 'Students':
                    self._delete_with_relations(c, 'Students', id, 'StudentsID')
                elif table_name == 'Subjects':
                    self._delete_with_relations(c, 'Subjects', id, 'SubjectsID')
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
        with self.conn.cursor() as c:
            c.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s", (table_name,))
            columns_info = c.fetchall()

            for _ in range(count):
                columns, values = self._generate_row_data(c, table_name, columns_info)

                if columns and values:
                    insert_query = f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({", ".join(values)})'
                    try:
                        c.execute(insert_query)
                        self.conn.commit()
                    except psycopg2.Error as e:
                        print(f"Error inserting row: {e}")
                        self.conn.rollback()

    def _validate_foreign_key(self, cursor, table, column, value):
        cursor.execute(f'SELECT "{column}" FROM "{table}" WHERE "{column}" = %s', (value,))
        return cursor.fetchone() is not None

    def _delete_with_relations(self, cursor, table, id, foreign_key):
        cursor.execute(f'SELECT "ID_connected" FROM "Students-subjects" WHERE "{foreign_key}" = %s', (id,))
        ss_ids = [row[0] for row in cursor.fetchall()]

        for ss_id in ss_ids:
            cursor.execute('DELETE FROM "Grades" WHERE "ConnectedID" = %s', (ss_id,))

        cursor.execute(f'DELETE FROM "Students-subjects" WHERE "{foreign_key}" = %s', (id,))
        cursor.execute(f'DELETE FROM "{table}" WHERE "ID" = %s', (id,))

    def _generate_row_data(self, cursor, table_name, columns_info):
        columns = []
        values = []

        for column_info in columns_info:
            column_name, column_type = column_info

            columns.append(f'"{column_name}"')

            if column_name == 'ID_connected' and table_name == 'Students-subjects':
                cursor.execute('SELECT COALESCE(MAX("ID_connected"), 0) FROM "Students-subjects"')
                max_id = cursor.fetchone()[0]
                values.append(str(max_id + 1))

            elif column_name == 'ID':
                cursor.execute(f'SELECT COALESCE(MAX("ID"), 0) FROM "{table_name}"')
                max_id = cursor.fetchone()[0]
                values.append(str(max_id + 1))

            elif column_name == 'StudentsID':
                cursor.execute('SELECT "ID" FROM "Students" ORDER BY RANDOM() LIMIT 1')
                student_id = cursor.fetchone()
                if student_id:
                    values.append(str(student_id[0]))

            elif column_name == 'SubjectsID':
                cursor.execute('SELECT "ID" FROM "Subjects" ORDER BY RANDOM() LIMIT 1')
                subject_id = cursor.fetchone()
                if subject_id:
                    values.append(str(subject_id[0]))

            elif column_name == 'ConnectedID':
                cursor.execute('SELECT "ID_connected" FROM "Students-subjects" ORDER BY RANDOM() LIMIT 1')
                connected_id = cursor.fetchone()
                if connected_id:
                    values.append(str(connected_id[0]))

            elif column_name == 'Value' and table_name == 'Grades':
                values.append(str(random.randint(1, 100)))

            elif column_type == 'integer':
                values.append(str(random.randint(1, 100)))

            elif column_type == 'character varying':
                values.append(f"'Test_{random.randint(1, 1000)}'")

        return columns, values

