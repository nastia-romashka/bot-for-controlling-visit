# Файл для создания парсера
from bs4 import BeautifulSoup
import requests
from loguru import logger
import sys
import json
import os

logger.remove()
logger.add(sys.stderr, level="DEBUG")


class Lessons():

    def __init__(self, group: int, type: str, name: str) -> None:
        self.lesson: list = [group, type, name]

    def __getitem__(self, item: int):
        return self.lesson[item]

    def __eq__(self, other: 'Lessons'):
        for i in range(len(self.lesson)):
            if self.lesson[i] != other[i]:
                return False
        return True

    def __str__(self) -> str:
        return str(self.lesson)

    def __repr__(self) -> str:
        return f'{self.lesson}'


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

    # Функция для проверки номера группы
    def get_groups(self, group: str):
        # Ищем HTML элемент, содержащий список групп
        group_raw = self.bs.find('div', 'form').find_all('span')[0].find_next()
        # Извлекаем текст из найденных элементов и фильтруем ненужные значения
        group_list = [x.text for x in group_raw if x.text not in ('- нет -', '\n')]
        # Если передана конкретная группа, ищем ее в списке и возвращаем результат
        if group:
            if group in group_list:
                return True
            else:
                return False

    def __separator_names_and_post(self, nap: str) -> list[str]:
        fio_arr = []
        fio_arr.append(nap[:nap.find(' ')])
        nap = nap[nap.find(' ') + 1:]
        fio_arr.append(nap[:nap.find('.')])
        nap = nap[nap.find('.') + 1:]
        fio_arr.append(nap[:nap.find('.')])
        nap = nap[nap.find('.'):]
        fio_arr.append(nap[nap.rfind('-') + 2:])
        return fio_arr

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

    def get_names_and_post_arr(self, name: str, index: int = 0) -> list[str]:

        try:
            # Обработка имени для предотвращения ошибок из-за опечаток
            # Все имена приводятся к нижнему регистру и удаляются все пробелы и точки
            name = name.replace(" ", "")
            name = name.replace('.', '')
            name = name.replace(',', '')
            name = name.lower()

            with open("all_teachers_names.json", "r") as file:
                names: dict = json.load(file)
            return self.__separator_names_and_post(names[name][index])

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
    def search_groups_and_lessons(self, name: str, num: int = 0):
        try:
            response_def = requests.get(self.URL + f'?p={self.get_index_teacher(name, num)}')
            bs_def = BeautifulSoup(response_def.text, "lxml")
            lessons = bs_def.find_all('div', 'study')
            groups_lessons = []

            for el in lessons:
                if len(el.find('span', "groups").text) <= 12:
                    gr = el.find('span', "groups").text
                    les = el.find('span').text
                    tip = el.find("b").find_next_sibling("b").text if el.find('b').text in '▲▼' else el.find('b').text
                    l: Lessons = Lessons (int(gr[gr.find(':') + 2:]), tip, les[les.find('–') + 2:les.rfind('–') - 2])
                    if not (l in groups_lessons):
                        groups_lessons.append(l)

                else:
                    grs: str= el.find('span', "groups").text
                    les = el.find('span').text
                    tip = el.find("b").find_next_sibling("b").text if el.find('b').text in '▲▼' else el.find('b').text
                    grs = grs[grs.find(':') + 2:]
                    grs_arr = grs.split('; ')
                    for g in grs_arr:
                        l: Lessons = Lessons(int(g), tip, les[les.find('–') + 2:les.rfind('–') - 2])
                        if not (l in groups_lessons):
                            groups_lessons.append(l)

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
    logger.debug(Pars.get_names_and_post_arr('Агапудов Д.В.'))
    logger.debug(Pars.search_lessons('Аграновский А.В.'))
    logger.debug(Pars.search_groups('Аграновский А.В.'))
    logger.debug(Pars.search_groups_and_lessons('Акопян Б К'))
    logger.debug(Pars.search_groups_and_lessons('Аграновский А.В.'))
