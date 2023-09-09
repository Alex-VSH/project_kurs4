from classes import HeadHunterAPI, SuperJobAPI, Vacancy, JSONSaver

# Создание экземпляра класса для работы с API сайтов с вакансиями
hh_api = HeadHunterAPI()
superjob_api = SuperJobAPI()

# Создание экземпляра класса для сохранения информации по вакансиям
json_saver = JSONSaver()


# Функция взаимодействия с пользователем
def user_interaction():
    search_query = input("Хотите найти работу? Введите поисковый запрос: ")
    job_platforms = input("Выберите платформы для поиска вакансий через запятую (HeadHunter, SuperJob): ")
    job_platforms_formatted = job_platforms.replace(' ', '')   # Форматируем ввод платформ
    job_platforms_formatted = job_platforms_formatted.split(',')
    if job_platforms_formatted not in [['HeadHunter'], ['SuperJob'], ['SuperJob', 'HeadHunter'], ['HeadHunter',
                                                                                                  'SuperJob']]:
        return print('Вы неверно указали платформы, программа прекращает работу')
    json_saver.get_vacancies(job_platforms_formatted, hh_api, superjob_api, search_query) # Обработка запроса по платформам

    Vacancy.append_vacancies() # Заполняем список экземпляров класса
    city_query = input("Введите название города: ")
    Vacancy.sort_by_city(city_query) # Сортируем вакансии по городу
    sort_query = input('Хотите отсортировать вакансии по зарплате? (да/нет) ')
    if sort_query not in ['нет', 'да']:
        return print('Некорректный ответ, программа прекращает работу')
    if sort_query == 'да':
        salary_query_one = input("Хотите видеть вакансии без зарплаты? (да/нет) ")
        if salary_query_one not in ['нет', 'да']:
            return print('Некорректный ответ, программа прекращает работу')
        if salary_query_one == 'нет':
            salary_query_two = int(input("Введите минимальную зарплату: "))
            Vacancy.remove_null_salary() # Убираем вакансии с нулевой ЗП
            Vacancy.sort_by_min_salary(salary_query_two) # Убираем вакансии с ЗП ниже указанной
        reverse_query = input('Введите порядок сортировки (возрастание/убывание): ')
        if reverse_query not in ['возрастание', 'убывание']:
            return print('Некорректный ответ, программа прекращает работу')
        Vacancy.sort_by_salary(reverse_query)
    top_n_query = int(input("Введите количество вакансий для вывода в топ N: "))
    Vacancy.show_top_n_vacancies(top_n_query)


if __name__ == "__main__":
    user_interaction()
