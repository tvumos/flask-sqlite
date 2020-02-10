# flask-sqlite

###Тестовый проект для изучения возможностей Flask.

Сайт предназначен для поиска результатов выборов Мэра Москвы в 2018 году

Результаты динамически загружаются с сайта МГИК:
http://www.moscow_city.izbirkom.ru/

Для поиска результатов голосования по любому УИК необходимо перейти на страницу "Поиск" и заполнить параметры поиска.
Реализовано кэширование списков Регионов и списков УИК для ускорения загрузки списочных полей на странице Поиск.
Реализовано динамическое присвоение атрибутов disabled/enabled для элементов управления.

Для сохранения результатов используется база данны SQLite.
Таблицы:
city - справочник городов
voting - список голосований
areas - районные территориальные избирательные комисиии
uiks - участковые избирательные комисии
description_fields - описание строк таблицы результатов
result - результаты голосования по каждому УИК

Реализован алгоритм поиска результатов голосования в таблице result. При наличии результатов по конкретному УИК данные
для отображения на сейте берутся из базы данных. В случае отсутствия сохраненных данных в таблице получаем данные
для отображения с сайта МГИК и сохраняем в таблицу result.

Требуемые библиотеки для работы программы указаны в файле:
requirement.txt 
