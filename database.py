import pymysql
from loguru import logger
from config import host, password, user, db_name

class DataBase:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host=host,
                port=3306,
                user=user,
                password=password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("Conection successful")
        except Exception as ex:
            logger.warning("Connection error")
            logger.warning(ex)

    ### Сreate tables ###
    def create_tables(self):
        try:
            with self.connection.cursor() as cursor:
                create_table_subject = (
                    "CREATE TABLE IF NOT EXISTS subject (idsubject INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                    "subjectName varchar(30) NOT NULL);")
                cursor.execute(create_table_subject)

                create_table_student = ("CREATE TABLE IF NOT EXISTS student (idstudent INT NOT NULL PRIMARY KEY, "
                                        "studentGroup INT NOT NULL, "
                                        "studentSurname VARCHAR(45) NOT NULL, "
                                        "studentName VARCHAR(45) NOT NULL, "
                                        "studentPatronymic VARCHAR(45) NULL, "
                                        "studentTelegram_id INT NOT NULL);")
                cursor.execute(create_table_student)

                create_table_teacher = (
                    "CREATE TABLE IF NOT EXISTS teacher (idteacher INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                    "teacherTelegram_id INT NOT NULL, "
                    "teacherSurname VARCHAR(30) NOT NULL, "
                    "teacherName VARCHAR(30) NOT NULL, "
                    "teacherPatronymic VARCHAR(30) NULL, "
                    "teacherPosition VARCHAR(30) NOT NULL, "
                    "teacherPassword VARCHAR(64) NOT NULL);")
                cursor.execute(create_table_teacher)

                create_table_shedule = (
                    "CREATE TABLE IF NOT EXISTS shedule (idshedule INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                    "idsubject INT NOT NULL, FOREIGN KEY(idsubject) REFERENCES subject(idsubject), "
                    "idteacher INT NOT NULL, FOREIGN KEY(idteacher) REFERENCES teacher(idteacher), "
                    "sheduletype VARCHAR(30) NOT NULL,"
                    "sheduleGroup INT NOT NULL);")
                cursor.execute(create_table_shedule)

                create_table_gradebook = (
                    "CREATE TABLE IF NOT EXISTS gradebook (idgradebook INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                    "idshedule INT NOT NULL, FOREIGN KEY(idshedule) REFERENCES shedule(idshedule),"
                    "idstudent INT NOT NULL, FOREIGN KEY(idstudent) REFERENCES student(idstudent),"
                    "gradebook5 INT NOT NULL,"
                    "gradebook4 INT NOT NULL,"
                    "gradebook3 INT NOT NULL,"
                    "gradebook2 INT NOT NULL,"
                    "gradebookAverage FLOAT NOT NULL,"
                    "gradebookVisits INT NOT NULL);")
                cursor.execute(create_table_gradebook)

                create_table_admin = ("CREATE TABLE IF NOT EXISTS admin (idadmin INT NOT NULL,"
                                      "adminTelegram_id INT NOT NULL,"
                                      "adminPassword INT NOT NULL);")
                cursor.execute(create_table_admin)
                logger.info("Tables created successfully")

        except Exception as ex:
            logger.warning("Tables creation error")
            logger.warning(ex)

    ### update data in db ###
    def update_data_in_db(self, table: str, parameter: str):
        try:
            with self.connection.cursor() as cursor:
                set_to: str = input("What to change the value to: ")
                set_to = '"' + set_to + '"'
                id: str = input("In which id to change: ")
                update_subject = f"UPDATE {table} SET {parameter} = {set_to} WHERE id{table} = {id};"
                cursor.execute(update_subject)
                self.connection.commit()
                logger.info("Data updated successfully")
        except Exception as ex:
            logger.warning("Data updating error")
            logger.warning(ex)

    ### add data in db ###
    def add_subject_in_db(self):
        try:
            with self.connection.cursor() as cursor:
                subName: str = input("Enter the name of the subject: ")
                subName = '"' + subName + '"'
                insert_query = f"INSERT INTO subject(subjectName) VALUES ({subName});"
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Subject added Successfully")
        except Exception as ex:
            logger.warning("Subject adding error")
            logger.warning(ex)

    def add_student_in_db(self, tg_id: int):
        try:
            with self.connection.cursor() as cursor:
                id: int = int(input("Enter id of the student: "))
                group: str = input("Enter group of the student: ")
                surname: str = input("Enter surname of the student: ")
                surname = '"' + surname + '"'
                name: str = input("Enter name of the student: ")
                name = '"' + name + '"'
                patronymic: str = input("Enter patronymic of the student (if there is no patronymic, enter No): ")
                if patronymic != "No":
                    patronymic = '"' + patronymic + '"'
                else:
                    patronymic = "Null"
                insert_query = (f"INSERT INTO student(idstudent, studentGroup, studentSurname, "
                                f"studentName, studentPatronymic, studentTelegram_id) "
                                f"VALUES ({id}, {group}, {surname}, {name}, {patronymic}, {tg_id});")
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Student added Successfully")
        except Exception as ex:
            logger.warning("Student adding error")
            logger.warning(ex)

    def add_teacher_in_db(self, tg_id: int, password: str):
        try:
            with self.connection.cursor() as cursor:
                surname: str = input("Enter surname of the teacher: ")
                surname = '"' + surname + '"'
                name: str = input("Enter name of the teacher: ")
                name = '"' + name + '"'
                patronymic: str = input("Enter patronymic of the teacher (if there is no patronymic, enter No): ")
                if patronymic == "No":
                    patronymic = "Null"
                else:
                    patronymic = '"' + patronymic + '"'
                position: str = input("Enter position of the teacher: ")
                position = '"' + position + '"'
                insert_query = (f"INSERT INTO teacher(teacherTelegram_id, teacherSurname, "
                                f"teacherName, teacherPatronymic, teacherPosition, teacherPassword) "
                                f"VALUES ({tg_id}, {surname}, {name}, {patronymic}, {position}, {password});")
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Teacher added Successfully")
        except Exception as ex:
            logger.warning("Teacher adding error")
            logger.warning(ex)

    def add_shedule_in_db(self):
        try:
            with self.connection.cursor() as cursor:
                idsubject: int = int(input("Enter subject id: "))
                idteacher: int = int(input("Enter teacher id: "))
                type: str = input("Enter type of lesson: ")
                type = '"' + type + '"'
                group: int = int(input("Enter group: "))
                insert_query = (f"INSERT INTO shedule(idsubject, idteacher, "
                                f"sheduletype, sheduleGroup) "
                                f"VALUES ({idsubject}, {idteacher}, {type}, {group});")
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Shedule added Successfully")
        except Exception as ex:
            logger.warning("Shedule adding error")
            logger.warning(ex)

    def add_admin_in_db(self, tg_id: int, Password: int):
        try:
            with self.connection.cursor() as cursor:
                id: int = int(input("Enter admin id: "))
                insert_query = (f"INSERT INTO admin(idadmin, adminTelegram_id, adminPassword) "
                                f"VALUES ({id}, {tg_id}, {password});")
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Admin added Successfully")
        except Exception as ex:
            logger.warning("Admin adding error")
            logger.warning(ex)

    ### view data in db ###
    def view_data_in_db(self, table: str):
        try:
            with self.connection.cursor() as cursor:
                view_data = f"Select * FROM {table}"
                cursor.execute(view_data)
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
                logger.info("Data viewed successfully")
        except Exception as ex:
            logger.warning("Data viewing error")
            logger.warning(ex)

    ### delete data in db ###
    def delete_data_in_db(self, table: str):
        try:
            with self.connection.cursor() as cursor:
                delete_id: str = input("Select id for deletion: ")
                delete_subject = f"DELETE FROM {table} WHERE id{table} = {delete_id};"
                cursor.execute(delete_subject)
                self.connection.commit()
                logger.info("Data deleted successfully")
        except Exception as ex:
            logger.warning("Data deletion error")
            logger.warning(ex)

    ### close db ###
    def close(self):
        try:
            self.connection.close()
            logger.info("Connection closed")
        except Exception as ex:
            logger.warning("Connection already closed")
            logger.warning(ex)
