import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

age = ctrl.Antecedent(np.arange(18, 100, 1), 'age')
jobs = ctrl.Antecedent(np.arange(0, 10, 1), 'jobs')
salary = ctrl.Consequent(np.arange(1500, 10000, 500), 'salary')

age['young'] = fuzz.trimf(age.universe, [18, 18, 35])
age['middle aged'] = fuzz.trimf(age.universe, [30, 40, 50])
age['old'] = fuzz.trimf(age.universe, [45, 65, 65])

jobs['few'] = fuzz.trimf(jobs.universe, [0, 0, 2])
jobs['medium'] = fuzz.trimf(jobs.universe, [1, 4, 6])
jobs['many'] = fuzz.trimf(jobs.universe, [5, 10, 10])

salary['low'] = fuzz.trimf(salary.universe, [1500, 1500, 2500])
salary['medium'] = fuzz.trimf(salary.universe, [2000, 5000, 7000])
salary['high'] = fuzz.trimf(salary.universe, [6000, 10000, 10000])
salary.view()
rules = []
rules.append(ctrl.Rule(age['young'] | jobs['few'], salary['low']))
rules.append(ctrl.Rule(age['middle aged'] & jobs['many'], salary['high']))
rules.append(ctrl.Rule(age['middle aged'] | jobs['medium'], salary['medium']))
rules.append(ctrl.Rule(age['middle aged'] & jobs['few'], salary['low']))
rules.append(ctrl.Rule(age['old'] | jobs['many'], salary['high']))

navigation_ctrl = ctrl.ControlSystem(rules)

fis = ctrl.ControlSystemSimulation(navigation_ctrl)

age = 35
jobs =1
fis.input['age'] = age
fis.input['jobs'] = jobs
fis.compute()
print("Age: " + str(age))
print("Jobs: " + str(jobs))
print(fis.output['salary'])
