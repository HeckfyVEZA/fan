import pandas as pd
import streamlit as st
from numpy import pi, array, interp
import matplotlib.pyplot as plt

def find_intersection(x1_array, y1_array, x2_array, y2_array, x0, min_rate, max_rate):
        func_1 = lambda x: interp(x, x1_array, y1_array) #if x >= 0 else -1e40
        func_2 = lambda x: interp(x, x2_array, y2_array) #if x >= 0 else -1e50
        # st.write(func_1(x0)-func_2(x0))
        # real_x = scipy.optimize.fsolve(lambda x: func_1(x) - func_2(x), x0, xtol=1e-4)
        # st.write(real_x)
        # st.write(func_1(real_x)-func_2(real_x))
        for x in range(int(min_rate), int(max_rate) + 1):
            if abs(func_1(x)-func_2(x)) < 0.5:
                real_x = x
                break
        return [real_x, func_2(real_x)]

data = {
    "phi_min": 1.60797e-5,
    "phi_max": 0.310177501,
    "a0_psi": -207.2339513,
    "a1_psi": 112.1828745,
    "a2_psi": -26.61097886,
    "a3_psi": 1.600108406,
    "a4_psi": 0.634921612,
    "a0_lmbd": -33.45169365,
    "a1_lmbd": 13.96405943,
    "a2_lmbd": -2.214217134,
    "a3_lmbd": 0.304536701,
    "a4_lmbd": 0.108375692,
    "rotation_frequency": 1680,
    "wheel_diameter": 630
}
st.set_page_config(layout="wide")

st.header("Кондиционер ВЕРОСА-600-102-У3 251006829б-СПБ")
cols = st.columns(2)
# phis = array([i for i in range(data["phi_min"], data["phi_max"], (data["phi_max"] - data["phi_min"])/20)])
ndots = 1000
phis = array(
    [
       data["phi_min"] + i * (data["phi_max"] - data["phi_min"]) / ndots for i in range(ndots + 1)  
    ]
)
psis = (
    data["a0_psi"] * phis ** 4
    + data["a1_psi"] * phis ** 3
    + data["a2_psi"] * phis ** 2
    + data["a3_psi"] * phis ** 1
    + data["a4_psi"] * phis ** 0
)
lmbds = (
    data["a0_lmbd"] * phis ** 4
    + data["a1_lmbd"] * phis ** 3
    + data["a2_lmbd"] * phis ** 2
    + data["a3_lmbd"] * phis ** 1
    + data["a4_lmbd"] * phis ** 0
)
# st.write(psis)
air_dencity = cols[0].number_input("Плотность воздуха в кг/м³", value=1.2, min_value=0.1)

air_flow = cols[0].number_input("Расход воздуха в м³/ч", value=1000, min_value=1)

pressure = cols[0].number_input("Напор в Па", value=100, min_value=0)

real_rotation_frequency = cols[0].number_input("Частота вращения рабочего колеса в об/мин", value=data["rotation_frequency"], min_value=1)

# Расчёт характерной (ометаемой) площади рабочего колеса
basic_wheel_area = (pi / 4) * (data["wheel_diameter"] / 1000) ** 2

# Расчёт окружной скорости рабочего колеса
circular_velocity = pi * real_rotation_frequency * data["wheel_diameter"] / 60_000

# Расчёт расхода воздуха (производительности вентилятора)
airflows = basic_wheel_area * circular_velocity * phis * 3600

# Расчёт статического давления
pressures = (psis * air_dencity * circular_velocity ** 2) / 2

# Расчёт коэффициента сети
k = pressure / (air_flow ** 2)

# Расчёт Мощности потребляемой
ns = air_dencity * basic_wheel_area * lmbds * circular_velocity ** 3 * .0005
N = lambda x: interp(x, airflows, ns)

given_airflow = airflows * 0 + air_flow
given_pressure = pressures * 0 + pressure
curve = k * airflows ** 2

dataframe = pd.DataFrame({
    "x": airflows,
    "y": pressures,
    "gx": given_airflow,
    "gy": given_pressure,
    "curve": curve
})
fig = plt.figure()
plt.plot(airflows, pressures, color="green")
plt.plot(airflows, curve)
plt.scatter(air_flow, pressure)

rx, ry = find_intersection(
        airflows,
        pressures,
        airflows,
        curve,
        pressure,
        min(airflows),
        max(airflows)
)
plt.scatter(rx, ry)
plt.xlabel("Расход воздуха [м³/ч]")
plt.ylabel("Давление [Па]")
plt.ylim(0, max(pressures) * 1.1)
plt.xlim(0, max(airflows) * 1.1)
plt.title('Кривая вентилятора')
plt.grid(True)
cols[1].pyplot(fig, use_container_width=True)
cols[0].write(f"<b>Действительные параметры:</b> <br>Расход <b>{int(round(rx, 0))}</b> м³/ч, \n<br>Давление <b>{int(round(ry, 0))}</b> Па, \n<br>Мощность <b>{round(N(int(round(rx, 0))), 3)}</b> кВт", unsafe_allow_html=True)
