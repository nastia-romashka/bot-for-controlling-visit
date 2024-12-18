import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def create_dashboard(df: pd.DataFrame, path: str):
    # Настройка градиента
    colors = [(230 / 255, 23 / 255, 76 / 255), (32 / 255, 86 / 255, 174 / 255)]
    cmap = LinearSegmentedColormap.from_list("custom_gradient", colors)
    gradient_palette = [cmap(i) for i in np.linspace(0, 1, len(df))]

    # Настройка сетки субплотов
    fig = plt.figure(figsize=(12, 10))
    gridspec = fig.add_gridspec(2, 2, height_ratios=[1, 1.5])

    # Верхний левый график
    ax1 = fig.add_subplot(gridspec[0, 0])
    sns.barplot(data=df, x="studentSurname", y="gradebookVisits", hue="studentSurname", palette=gradient_palette,
                ax=ax1)
    # Добавление подписей для всех контейнеров на ax2
    if ax1.containers:
        for container in ax1.containers:  # Перебираем все контейнеры
            ax1.bar_label(container, fontsize=10)

    ax1.set_title("Посещения")


    # Верхний правый график
    ax2 = fig.add_subplot(gridspec[0, 1])
    sns.barplot(data=df, x="average_grade", y="studentSurname",hue="studentSurname", palette=gradient_palette, ax=ax2)
    # Добавление подписей для всех контейнеров на ax2
    if ax2.containers:
        for container in ax2.containers:  # Перебираем все контейнеры
            ax2.bar_label(container, fontsize=10)

    ax2.set_title("Средняя оценка")

    # Преобразование данных в длинный формат
    long_df = df.melt(
        id_vars=["studentSurname"],
        value_vars=["gradebook5", "gradebook4", "gradebook3", "gradebook2"],
        var_name="Оценка",
        value_name="Количество"
    )
    long_df["Оценка"] = long_df["Оценка"].str.extract(r'(\d)').astype(int)

    # Нижний график
    ax3 = fig.add_subplot(gridspec[1, :])
    hue_order = long_df["studentSurname"].unique()
    colors_for_hue = {name: cmap(i / (len(hue_order) - 1)) for i, name in enumerate(hue_order)}
    sns.barplot(
        data=long_df,
        x="Оценка",
        y="Количество",
        hue="studentSurname",
        palette=colors_for_hue,
        ax=ax3
    )
    ax3.set_title("Распределение оценок")
    ax3.legend(title="Фамилия студента", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Общий заголовок и оформление
    plt.suptitle("Информация по группе", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(path)

if __name__ == '__main__':
    data = {
        'studentTelegram_id': [421901315, 421901316, 421901317, 421901318, 421901319],
        'studentSurname': ['Борисов', 'Иванов', 'Петров', 'Сидоров', 'Кузнецов'],
        'studentName': ['Э', 'И', 'П', 'С', 'К'],
        'studentPatronymic': ['Е', 'А', 'Н', 'И', 'Д'],
        'gradebookVisits': [10, 5, 7, 2, 4],
        'gradebook5': [5, 4, 3, 5, 2],
        'gradebook4': [4, 3, 5, 2, 4],
        'gradebook3': [3, 2, 4, 3, 5],
        'gradebook2': [2, 3, 2, 4, 3],
        'average_grade': [10, 9, 8, 7, 6]
    }

    df = pd.DataFrame(data)

    create_dashboard(df,"dashboard.png")
