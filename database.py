# Файл для создания базы данных
import pymysql
from pymysql import cursors
from loguru import logger
from config import host, password, user, db_name


class DataBase:
    def __init__(self):
        try:
            try:
                self.connection = pymysql.connect(
                    host=host,
                    port=3306,
                    user=user,
                    password=password,
                    database=db_name,
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info("Connection successful")
            except:
                self.connection = pymysql.connect(
                    host=host,
                    port=3306,
                    user=user,
                    password=password,
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info("Connection successful (without db)")
                with self.connection.cursor() as cursor:
                    create_db = "CREATE DATABASE " + db_name
                    cursor.execute(create_db)
                    logger.info("Database creation successful")
                self.connection = pymysql.connect(
                    host=host,
                    port=3306,
                    user=user,
                    password=password,
                    database=db_name,
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info("Connection successful")
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
    ### array[0] - Параметр, в котором будет изменение в таблице
    ### array[1] - На что поменять значение параметра
    ### array[2] - id, в котором поменяется значение
    def update_data_in_db(self, table: str, array: list):
        try:
            with self.connection.cursor() as cursor:
                array[1] = '"' + array[1] + '"'
                update_subject = f"UPDATE {table} SET {array[0]} = {array[1]} WHERE id{table} = {array[2]};"
                cursor.execute(update_subject)
                self.connection.commit()
                logger.info("Data updated successfully")
        except Exception as ex:
            logger.warning("Data updating error")
            logger.warning(ex)

    ### add data in db ###
    def add_subject_in_db(self, subName: str):
        try:
            with self.connection.cursor() as cursor:
                subName = '"' + subName + '"'
                insert_query = f"INSERT INTO subject(subjectName) VALUES ({subName});"
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Subject added Successfully")
        except Exception as ex:
            logger.warning("Subject adding error")
            logger.warning(ex)

    ### array[0] - id студента (номер студ. билета)
    ### array[1] - Группа студента
    ### array[2] - Фамилия студента
    ### array[3] - Имя студента
    ### array[4] - Отчество студента
    def add_student_in_db(self, array: list,tg_id: int):
        try:
            with self.connection.cursor() as cursor:
                array[2] = '"' + array[2] + '"'
                array[3] = '"' + array[3] + '"'
                if array[4] != "No":
                    array[4] = '"' + array[4] + '"'
                else:
                    array[4] = "Null"
                insert_query = (f"INSERT INTO student(idstudent, studentGroup, studentSurname, "
                                f"studentName, studentPatronymic, studentTelegram_id) "
                                f"VALUES ({array[0]}, {array[1]}, {array[2]}, {array[3]}, {array[4]}, {tg_id});")
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Student added Successfully")
        except Exception as ex:
            logger.warning("Student adding error")
            logger.warning(ex)

    ### array[0] - Фамилия преподавателя
    ### array[1] - Имя преподавателя
    ### array[2] - Отчество преподавателя
    ### array[3] - Должность преподавателя
    def add_teacher_in_db(self, array: list, tg_id: int, password: str):
        try:
            with self.connection.cursor() as cursor:
                array[0] = '"' + array[0] + '"'
                array[1] = '"' + array[1] + '"'
                if array[2] == "No":
                    array[2] = "Null"
                else:
                    array[2] = '"' + array[2] + '"'
                array[3] = '"' + array[3] + '"'
                insert_query = (f"INSERT INTO teacher(teacherTelegram_id, teacherSurname, "
                                f"teacherName, teacherPatronymic, teacherPosition, teacherPassword) "
                                f"VALUES ({tg_id}, {array[0]}, {array[1]}, {array[2]}, {array[3]}, {password});")
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Teacher added Successfully")
        except Exception as ex:
            logger.warning("Teacher adding error")
            logger.warning(ex)

    ### array[0] - id предмета
    ### array[1] - id преподавателя
    ### array[2] - Тип занятия (лабораторная/лекция и т.п.)
    ### array[3] - Группа, у которой занятие
    def add_shedule_in_db(self, array: list):
        try:
            with self.connection.cursor() as cursor:
                array[2] = '"' + array[2] + '"'
                insert_query = (f"INSERT INTO shedule(idsubject, idteacher, "
                                f"sheduletype, sheduleGroup) "
                                f"VALUES ({array[0]}, {array[1]}, {array[2]}, {array[3]});")
                cursor.execute(insert_query)
                self.connection.commit()
                logger.info("Shedule added Successfully")
        except Exception as ex:
            logger.warning("Shedule adding error")
            logger.warning(ex)

    def add_admin_in_db(self, tg_id: int, password: int):
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
    def delete_data_in_db(self, table: str, id: int):
        try:
            with self.connection.cursor() as cursor:
                delete_subject = f"DELETE FROM {table} WHERE id{table} = {id};"
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