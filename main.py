import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import cProfile


def main():
    # Создаем универсум дискурса для выполненного плана от 0 до 100 источников
    done_plan = ctrl.Antecedent(np.arange(0, 101, 1), 'done_plan')
    # Создаем универсум дискурса для региона (0 - мск-спб, 1 - новые, 2 - ост)
    region = ctrl.Antecedent(np.arange(0, 3, 1), 'region')
    # Создаем универсум дискурса для опыта (0 - маленький, 1 - средний, 2 - большой)
    experience = ctrl.Antecedent(np.arange(0, 3, 1), 'experience')
    # Создаем универсум дискурса для внеплановой работы от 0 до 50 часов
    over_work = ctrl.Antecedent(np.arange(0, 51, 1), 'over_work')
    # Создаем универсум дискурса для сложности источников (0 - нет сложных источников, 1 - есть сложные источники)
    difficulty_of_item = ctrl.Antecedent(np.arange(0, 2, 1), 'difficulty_of_item')
    # Создаем универсум дискурса для действия (0 - платить полную сумму, 1 - платить меньше плана)
    pay_salary = ctrl.Consequent(np.arange(0, 2, 1), 'pay_salary')

    # Определяем функции принадлежности для выполненного плана
    done_plan['не выполнен'] = fuzz.trapmf(done_plan.universe, [0, 0, 55, 65])
    done_plan['почти выполнен'] = fuzz.trapmf(done_plan.universe, [60, 71, 74, 74])
    done_plan['выполнен'] = fuzz.trapmf(done_plan.universe, [70, 75, 100, 100])

    # Определяем функции принадлежности для региона
    region['Москва-Питер'] = fuzz.trimf(region.universe, [0, 0, 1])
    region['Новые регионы'] = fuzz.trimf(region.universe, [0, 1, 2])
    region['Остальные'] = fuzz.trimf(region.universe, [1, 2, 2])

    # Определяем функции принадлежности для опыта работы
    experience['мало'] = fuzz.trimf(experience.universe, [0, 0, 1])
    experience['средне'] = fuzz.trimf(experience.universe, [0, 1, 2])
    experience['много'] = fuzz.trimf(experience.universe, [1, 2, 2])

    # Определяем функции принадлежности для внеплановой работы
    over_work['не учитывается'] = fuzz.trapmf(over_work.universe, [0, 0, 10, 20])
    over_work['слабое влияние'] = fuzz.trapmf(over_work.universe, [5, 15, 20, 30])
    over_work['сильное влияние'] = fuzz.trapmf(over_work.universe, [20, 30, 50, 50])

    # Определяем функции принадлежности для наличия сложных источников
    difficulty_of_item['есть'] = fuzz.trimf(difficulty_of_item.universe, [0, 0, 1])
    difficulty_of_item['нет'] = fuzz.trimf(difficulty_of_item.universe, [0, 1, 1])

    # Определяем функции принадлежности для действий
    pay_salary['Выплата меньшей суммы'] = fuzz.trimf(pay_salary.universe, [0, 0, 1])
    pay_salary['Выплата полной суммы'] = fuzz.trimf(pay_salary.universe, [0, 1, 1])

    # Определяем правила
    with open('rules.txt', 'r') as f:
        exec(f.read())

    rule_list = [v for k, v in locals().items() if k.startswith('rule')]

    # Создаем систему контроля и симулятор
    btn_ctrl = ctrl.ControlSystem(rule_list)
    btn_sim = ctrl.ControlSystemSimulation(btn_ctrl)

    # Примеры данных для тестирования
    test_cases = [
        {'done_plan1': 70, 'region1': 0, 'experience1': 0, 'over_work1': 5, 'difficulty_of_item1': 0},  #1
        {'done_plan1': 55, 'region1': 1, 'experience1': 2, 'over_work1': 41, 'difficulty_of_item1': 0},  #2
        {'done_plan1': 80, 'region1': 2, 'experience1': 0, 'over_work1': 11, 'difficulty_of_item1': 1},  #3
        {'done_plan1': 63, 'region1': 1, 'experience1': 2, 'over_work1': 7, 'difficulty_of_item1': 1},  #4
        {'done_plan1': 72, 'region1': 0, 'experience1': 1, 'over_work1': 31, 'difficulty_of_item1': 0},  #5
        {'done_plan1': 69, 'region1': 1, 'experience1': 1, 'over_work1': 9, 'difficulty_of_item1': 1},  #6
        {'done_plan1': 79, 'region1': 2, 'experience1': 0, 'over_work1': 23, 'difficulty_of_item1': 0},  #7
        {'done_plan1': 59, 'region1': 0, 'experience1': 1, 'over_work1': 40, 'difficulty_of_item1': 0},  # 8
        {'done_plan1': 71, 'region1': 1, 'experience1': 2, 'over_work1': 37, 'difficulty_of_item1': 1},  # 9
        {'done_plan1': 99, 'region1': 1, 'experience1': 1, 'over_work1': 1, 'difficulty_of_item1': 1},  # 10
    ]

    # Открываем файл для записи результатов
    with open('output.txt', 'w') as output_file:
        # Тестирование системы
        for case in test_cases:
            btn_sim.input['done_plan'] = case['done_plan1']
            btn_sim.input['region'] = case['region1']
            btn_sim.input['experience'] = case['experience1']
            btn_sim.input['over_work'] = case['over_work1']
            btn_sim.input['difficulty_of_item'] = case['difficulty_of_item1']
            btn_sim.compute()

            experience_dict = {0: 'маленьким', 1: 'средним', 2: 'большим'}
            difficulty_dict = {0: 'наличием', 1: 'отсутствием'}
            action_output = 'Выплатить полную сумму' if btn_sim.output['pay_salary'] > 0.5 else 'Выплатить меньшую сумму'

            # Запись результата в файл
            output_file.write(
                f"Сотруднику, который сделал: {case['done_plan1']} источников "
                f"по региону: {['Москва-Питер', 'Новые регионы', 'Остальные'][case['region1']]}, "
                f"обладающему  {experience_dict[case['experience1']]} опытом, "
                f"c внеплановой работой: {case['over_work1']} часов, "
                f"и {difficulty_dict[case['difficulty_of_item1']]} сложных источников "
                f"-> Действие: {action_output}\n"
            )


# Графическое отображение функций принадлежности
    done_plan.view()
    region.view()
    experience.view()
    pay_salary.view()
    over_work.view()
    difficulty_of_item.view()
    plt.show()


if __name__ == "__main__":
    cProfile.run("main()")
