# Файл для создания парсера
from bs4 import BeautifulSoup
import requests
from loguru import logger
import sys
import json
import os

logger.remove()
logger.add(sys.stderr, level="INFO")


class ParsingSUAIRasp:

    def __init__(self) -> None:
        # Ссылка на сайт с расписанием
        self.URL = f'https://guap.ru/rasp/'
        # Запрос к сайту
        self.requests = requests.get(self.URL)
        # Получение данных с сайта
        self.bs = BeautifulSoup(self.requests.text, "lxml")

        # Поиск всех имен и запись их в json файл
        if not (os.path.exists(r'all_teachers_names.json')):
            names_raw = self.bs.find('div', 'form').find_all('span')[1].find_next()

            names_list = [x.text for x in names_raw if x.text != ('- нет -')]
            final_names: dict[str][list[str]] = {}

            for el in names_list:
                key = el[:el.find("-") - 1].replace(" ", "")
                key = key.replace(".", "")
                key = key.lower()

                if key != '':
                    if key not in final_names:
                        final_names[key] = []
                    final_names[key].append(el)

            with open("all_teachers_names.json", "w") as file:
                json.dump(final_names, file, ensure_ascii=False)

            logger.info('JSON all_teachers_names created')

        # Поиск всех групп и запись их в json файл
        if not (os.path.exists(r'all_group.json')):
            group_raw = self.bs.find('div', 'form').find_all('span')[0].find_next()

            group_list = [x.text for x in group_raw if x.text != ('- нет -') and x.text != ('\n')]

            final_group: dict[str][list[str]] = {}
            final_group['groups'] = group_list

            with open("all_group.json", "w") as file:
                json.dump(final_group, file, ensure_ascii=False)

            logger.info('JSON all_group created')

    # Функция для получения имени и должности преподавателя по введенному имени
    def get_names_and_post(self, name: str) -> list[str]:

        try:

            # Обработка имени для предотвращения ошибок из-за опечаток
            # Все имена приводятся к нижнему регистру и удаляются все пробелы и точки
            name = name.replace(" ", "")
            name = name.replace('.', '')
            name = name.replace(',', '')
            name = name.lower()

            with open("all_teachers_names.json", "r") as file:
                names: dict = json.load(file)
            return names[name]

        except Exception as ex:
            logger.warning("There is no teacher with that name")
            logger.warning(ex)

    # Функция для получения номера преподавателя в списке на сайте
    def get_index_teacher(self, name: str, num: int) -> int:
        try:
            index = self.bs.find(name='option', string=self.get_names_and_post(name)[num])['value']
            return int(index)
        except Exception as ex:
            logger.warning("Index not received")
            logger.warning(ex)

    # Функция для получения группы и предмета по имени преподавателя
    def search_groups_and_lessons(self, name: str, num: int = 0, l_type: bool = False) -> (
            list[tuple[str, str]] | list[tuple[str, str, str]]):
        # Если l_type == True к выводу будет добавлен тип занятия
        try:
            response_def = requests.get(self.URL + f'?p={self.get_index_teacher(name, num)}')
            bs_def = BeautifulSoup(response_def.text, "lxml")

            lessons = bs_def.find_all('div', 'study')

            groups_lessons = []

            for el in lessons:
                gr = el.find('span', "groups").text
                les = el.find('span').text
                tip = el.find('b').text
                if l_type:
                    groups_lessons.append((gr[gr.find(':') + 2:], tip, les[les.find('–') + 2:les.rfind('–') - 2]))
                else:
                    groups_lessons.append((gr[gr.find(':') + 2:], les[les.find('–') + 2:les.rfind('–') - 2]))

            return groups_lessons

        except Exception as ex:
            logger.warning("There is no teacher with that name")
            logger.warning(ex)

    # Функция для поиска предметов преподавателя по имени
    def search_lessons(self, name: str, num: int = 0) -> list[str]:
        try:
            response_def = requests.get(self.URL + f'?p={self.get_index_teacher(name, num)}')
            bs_def = BeautifulSoup(response_def.text, "lxml")

            lessons = bs_def.find_all('div', 'study')

            lessons = [x.span.text for x in lessons]
            lessons = [x[x.find('–') + 2:x.rfind('–') - 2] for x in lessons]
            lessons = list(dict.fromkeys(lessons))
            return lessons
        except Exception as ex:
            logger.warning("There is no teacher with that name")
            logger.warning(ex)

    # Функция для поиска групп преподавателя по имени
    def search_groups(self, name: str, num: int = 0) -> list[str]:
        try:
            response_def = requests.get(self.URL + f'?p={self.get_index_teacher(name, num)}')
            bs_def = BeautifulSoup(response_def.text, "lxml")

            groups = bs_def.find_all('span', 'groups')
            groups = [x.a.text for x in groups]

            groups = list(dict.fromkeys(groups))

            return groups

        except Exception as ex:
            logger.warning("There is no teacher with that name")
            logger.warning(ex)


if __name__ == '__main__':
    Pars: ParsingSUAIRasp = ParsingSUAIRasp()
    logger.debug(Pars.get_names_and_post('Агапудов Д.В.'))
    logger.debug(Pars.search_lessons('Агапудов Д.В.'))
    logger.debug(Pars.search_groups('Агапудов Д.В.'))
    logger.debug(Pars.search_groups_and_lessons('Агапудов Д.В.', l_type=True))
