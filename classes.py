import json
import os
from abc import ABC, abstractmethod
import requests
import sys

# Используем secret key для superjob api
headers = {"X-Api-App-Id": os.getenv("API_SUPERJOB_KEY")}


class JobAPI(ABC):

    @abstractmethod
    def get_vacancies(self):
        pass

    @abstractmethod
    def create_vacancies_list(self):
        pass


class HeadHunterAPI(JobAPI):
    def get_vacancies(self, search_text):
        """Функция получения ответа от API"""
        self.url = 'https://api.hh.ru'
        params = {
            "text": search_text,
            "per_page": 40
        }
        response = requests.get(f'{self.url}/vacancies', params=params)
        return response.json()

    def create_vacancies_list(self, vacancies_info):
        """Функция преобразует ответ от API в список словарей с вакансиями"""
        vacancies_dict = []
        for vacancy_instance in vacancies_info['items']:
            requirements = vacancy_instance['snippet']['requirement']
            symbols_to_remove = ["<highlighttext>", "</highlighttext>"]  # Удаляем лишние символы из строки
            for symb in symbols_to_remove:
                try:
                    requirements = requirements.replace(symb, "")
                except AttributeError:
                    requirements = "Описание отсутствует"
            if vacancy_instance['salary'] is None or vacancy_instance['salary']['from'] is None:
                salary = 0
            else:
                salary = vacancy_instance['salary']['from']
            vacancy_data = {
                "name": vacancy_instance['name'],
                "url": vacancy_instance['alternate_url'],
                "salary": salary,
                "city": vacancy_instance['area']['name'],
                "requirements": f"{requirements}"
            }
            vacancies_dict.append(vacancy_data)
        return vacancies_dict


class SuperJobAPI(JobAPI):
    def get_vacancies(self, search_text):
        """Функция получения ответа от API"""
        self.url = 'https://api.superjob.ru'
        params = {
            "keyword": search_text,
            "page": 0,
            "count": 40
        }
        response = requests.get(f'{self.url}/2.0/vacancies/', headers=headers, params=params)
        return response.json()

    def create_vacancies_list(self, vacancies_info):
        """Функция преобразует ответ от API в список словарей с вакансиями"""
        vacancies_dict = []
        for vacancy_instance in vacancies_info['objects']:
            requirements = vacancy_instance['vacancyRichText']
            symbols_to_remove = ["<p>", "</li>", "<li>", "</p>", "<ul>", "</b>", "<b>", "\n", "<i>",
                                 "</i>"]  # Удаляем лишние символы из строки
            for symb in symbols_to_remove:
                try:
                    requirements = requirements.replace(symb, "")
                except AttributeError:
                    requirements = "Описание отсутствует"
            if vacancy_instance['payment_from'] == 0 or vacancy_instance['payment_from'] is None:
                vacancy_salary = 0
            else:
                vacancy_salary = vacancy_instance['payment_from']
            if vacancy_instance['address'] is None:
                vacancy_city = None
            else:
                vacancy_city = vacancy_instance['address'].split(',')[0]
            vacancy_data = {
                "name": vacancy_instance['profession'],
                "url": vacancy_instance['link'],
                "salary": vacancy_salary,
                "city": vacancy_city,
                "requirements": f"{requirements[:250]}..."
            }
            vacancies_dict.append(vacancy_data)
        return vacancies_dict


class Vacancy:
    all_vacancies = []

    def __init__(self, name, url, salary, city, requirements):
        self.name = name
        self.url = url
        self.salary = salary
        self.city = city
        self.requirements = requirements

        self.all_vacancies.append(self)

    def __eq__(self, other):
        return self.salary == other.salary

    def __lt__(self, other):
        return self.salary < other.salary

    def __gt__(self, other):
        return self.salary > other.salary

    @classmethod
    def append_vacancies(cls):
        with open('vacancies.json', "r", encoding='utf8') as json_file:
            vacancies = json.load(json_file)
            for vacancy in vacancies:
                Vacancy(**vacancy)

    @classmethod
    def sort_by_city(cls, city):
        i = 0  # Здесь операция в цикле т.к. почему-то не работает
        while i < 3:  # с первого раза
            for vacancy in cls.all_vacancies:
                if vacancy.city != city:
                    cls.all_vacancies.remove(vacancy)
            i += 1

    @classmethod
    def remove_null_salary(cls):
        for vacancy in cls.all_vacancies:
            if vacancy.salary == 0:
                cls.all_vacancies.remove(vacancy)

    @classmethod
    def sort_by_min_salary(cls, salary):
        i = 0  # Здесь операция в цикле т.к. почему-то не работает
        while i < 3:  # с первого раза
            for vacancy in cls.all_vacancies:
                if vacancy.salary < salary:
                    cls.all_vacancies.remove(vacancy)
            i += 1

    @classmethod
    def sort_by_salary(cls, answer):
        if answer == 'возрастание':
            reverse_value = False
            cls.all_vacancies.sort(reverse=reverse_value)
        elif answer == 'убывание':
            reverse_value = True
            cls.all_vacancies.sort(reverse=reverse_value)

    @classmethod
    def show_top_n_vacancies(cls, top_n_num):
        if len(cls.all_vacancies) >= top_n_num:
            for i in range(top_n_num):
                print(f'*** {cls.all_vacancies[i].name} ***\n'
                      f'Ссылка: {cls.all_vacancies[i].url}\n'
                      f'Зарплата: {cls.all_vacancies[i].salary}')
        else:
            for vacancy in cls.all_vacancies:
                print(f'*** {vacancy.name} ***\n'
                      f'Ссылка: {vacancy.url}\n'
                      f'Зарплата: {vacancy.salary}')
            print('Больше вакансий по вашим запросам не нашлось\n')


class FILESaver(ABC):
    @abstractmethod
    def create_vacancies_json(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class JSONSaver(FILESaver):
    def create_vacancies_json(self, list_one, list_two=None):
        """Функция собирает итоговую информацию по вакансиям и создает для нее JSON файл"""
        with open('vacancies.json', "w", encoding='utf8') as json_file:
            if not list_two:
                json_string = json.dumps(list_one, ensure_ascii=False, indent=4)
                json_file.write(json_string)
            else:
                merged_list = list_one + list_two
                json_string = json.dumps(merged_list, ensure_ascii=False, indent=4)
                json_file.write(json_string)

    def get_vacancies(self, job_platforms_formatted, hh_api, superjob_api, search_query):
        """Функция обрабатывает запрос пользователя по выбору платформы для поиска вакансий"""
        if job_platforms_formatted == ['HeadHunter']:
            hh_api_result = hh_api.get_vacancies(search_query)
            hh_api_list = hh_api.create_vacancies_list(hh_api_result)
            if hh_api_list == []:
                print('По вашему запросу ничего не найдено, программа прекращает работу')
                sys.exit(0)
            self.create_vacancies_json(hh_api_list)
        elif job_platforms_formatted == ['SuperJob']:
            superjob_api_result = superjob_api.get_vacancies(search_query)
            superjob_api_list = superjob_api.create_vacancies_list(superjob_api_result)
            if superjob_api_list == []:
                print('По вашему запросу ничего не найдено, программа прекращает работу')
                sys.exit(0)
            self.create_vacancies_json(superjob_api_list)
        elif job_platforms_formatted == ['SuperJob', 'HeadHunter'] or job_platforms_formatted == ['HeadHunter',
                                                                                                  'SuperJob']:
            hh_api_result = hh_api.get_vacancies(search_query)
            hh_api_list = hh_api.create_vacancies_list(hh_api_result)
            superjob_api_result = superjob_api.get_vacancies(search_query)
            superjob_api_list = superjob_api.create_vacancies_list(superjob_api_result)
            if superjob_api_list == [] and hh_api_list == []:
                print('По вашему запросу ничего не найдено, программа прекращает работу')
                sys.exit(0)
            self.create_vacancies_json(superjob_api_list, hh_api_list)


