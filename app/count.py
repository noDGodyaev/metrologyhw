#!/usr/bin/env python
# coding: utf-8
import numpy as np
import os.path
import scipy.stats


# Парамаетры вычисления
def calculate(filename, split, confidence):
    # split = 5  # На сколько групп разделить выборку
    # confidence = 0.05  # Confidence level (квантиль для F распределения)
    filepath = "UPLOAD_FOLDER/" + filename
    assert os.path.exists(filepath)  # Проверяем если файл существует
    assert split > 3  # Критерий деления
    full_array = read_file(filepath)  # Считываем файл из данных
    assert len(full_array) >= 6  # Если данных слишком мало, проводить эксперимент бесполезно

    list_of_groups = np.array_split(full_array, split)
    # разбиваем данные на s групп бприблизительно одинакового размера

    S_within, S_between = calculate_variances(list_of_groups)
    Ft = S_within / S_between
    Fq = get_critical_F(confidence, list_of_groups)
    err = False
    if Ft < Fq:
        print("\nСистематической погрешности не обнаружено")
        err = False
    else:
        print("\nОбнаружена систематическая погрешность!")
        err = True
    answer = [err, S_between, S_within, Ft, confidence, Fq]
    return answer


def read_file(path):
    """
    Считывает данные из файла и возвращает numpy массив цисел
    Важно: Предпологается что все числа расположены через пробел на одной строке!
           Код также предпологает что файл существует
    """
    with open(path) as fp:
        line = fp.readline()
        line = line.replace(",", ".")
        numbers = list(line.split())
        return np.array([float(i) for i in numbers])


def calculate_variances(groups):
    """
    Выщитывает средняю сумму дисперсий результатов наблюдений (S_within)
    И усредненную межсерийную дисперсию (S_between)
    Возжращает tuple (S_between, S_within)
    """
    # Общие Данные
    group_sizes = np.array([len(x) for x in groups])  # Количество элементов в каждой группы
    total_elements = np.sum(group_sizes)  # Полное количество элементов
    total_groups = len(group_sizes)  # Количество групп
    group_means = np.array([np.mean(x) for x in groups])  # Среднее в каждой группе
    total_mean = np.mean(group_means)  # Среднее по всем элементам всех групп

    # S_within
    group_variance = np.array([np.var(x) for x in groups])  # variance отличается от SUM(x_i - x_mean)^2 делением на N
    group_sswg = np.sum(group_sizes * group_variance)  # Нам это деление не нужно, поэтому мы уго анилируем умножением
    # Сумирием и получаем sum of sum of squares within each group
    S_within = group_sswg / (total_elements - total_groups)  # Средняя сумма дисперсий результатов наблюдений

    # S_between
    group_squares = np.square(group_means - total_mean)  # Список квадратов
    group_ssbq = np.sum(group_squares * group_sizes)  # Суммируем с весом
    S_between = group_ssbq / (total_groups - 1)  # Усредненная межсерийная дисперсия

    return (S_between, S_within)


# Note: total_mean === (1/N)*SUM[j=0,j=s](n_j * x_j_hat)      # Они эквивалентны.

def get_critical_F(a, groups):
    """
    Возвращает критичную F оценку при задоном уровне уверености "a"
    Обычно "a" задают такими: 0.01, 0.05, 0.1
    Требует импорта: scipy.stats
    """
    total_elements = sum([len(x) for x in groups])  # Полное количество элементов
    total_groups = len(groups)  # Количество групп

    return scipy.stats.f.ppf(q=1 - a, dfn=total_groups - 1, dfd=total_elements - total_groups)

