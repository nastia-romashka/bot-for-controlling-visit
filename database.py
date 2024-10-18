# Файл для создания базы данных
import pymysql
from config import host, password, user, db_name


try:
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Successfully connected...")
    print('_' * 30)


    try:
        # Сreating tables
        with connection.cursor() as cursor:
            create_table_subject = ("CREATE TABLE IF NOT EXISTS subject (idsubject INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                                    "subjectName varchar(30) NOT NULL);")
            cursor.execute(create_table_subject)

            create_table_student = ("CREATE TABLE IF NOT EXISTS student (idstudent INT NOT NULL PRIMARY KEY, "
                                    "studentGroup INT NOT NULL, "
                                    "studentSurname VARCHAR(45) NOT NULL, "
                                    "studentName VARCHAR(45) NOT NULL, "
                                    "studentPatronymic VARCHAR(45) NULL, "
                                    "studentTelegram_id INT NOT NULL);")
            cursor.execute(create_table_student)

            create_table_teacher = ("CREATE TABLE IF NOT EXISTS teacher (idteacher INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                                    "teacherTelegram_id INT NOT NULL, "
                                    "teacherSurname VARCHAR(30) NOT NULL, "
                                    "teacherName VARCHAR(30) NOT NULL, "
                                    "teacherPatronymic VARCHAR(30) NULL, "
                                    "teacherPosition VARCHAR(30) NOT NULL, "
                                    "teacherPassword VARCHAR(64) NOT NULL);")
            cursor.execute(create_table_teacher)

            create_table_shedule = ("CREATE TABLE IF NOT EXISTS shedule (idshedule INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                                    "idsubject INT NOT NULL, FOREIGN KEY(idsubject) REFERENCES subject(idsubject), "
                                    "idteacher INT NOT NULL, FOREIGN KEY(idteacher) REFERENCES teacher(idteacher), "
                                    "sheduletype VARCHAR(30) NOT NULL,"
                                    "sheduleGroup INT NOT NULL);")
            cursor.execute(create_table_shedule)

            create_table_gradebook = ("CREATE TABLE IF NOT EXISTS gradebook (idgradebook INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
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

        # ### example of data insertion ###
        # with connection.cursor() as cursor:
        #     insert_query = "INSERT INTO subject(subjectName) VALUES ('statistics'), ('english');"
        #     cursor.execute(insert_query)
        #     connection.commit()
        #
        # ### example of data update ###
        # with connection.cursor() as cursor:
        #     update_subject = "UPDATE subject SET subjectName = 'physics' WHERE subjectName = 'english';"
        #     cursor.execute(update_subject)
        #
        # ### example of data deletion ###
        # with connection.cursor() as cursor:
        #     delete_subject = "DELETE FROM subject WHERE idsubject = 1;"
        #     cursor.execute(delete_subject)
        #     connection.commit()
        #
        # ### example of data viewing ###
        # with connection.cursor() as cursor:
        #     view_subject_data = "Select * FROM subject"
        #     cursor.execute(view_subject_data)
        #     rows = cursor.fetchall()
        #     for row in rows:
        #         print(row)

    finally:
        connection.close()
        print("Connection closed...")


except Exception as ex:
    print("Connection refused...")
    print(ex)