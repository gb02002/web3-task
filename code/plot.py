import matplotlib.pyplot as plt


def make_plot(adjusted_price_1, adjusted_price_2):
    # Пример данных для визуализации
    pools = ['Пул 1 (WETH/USDT)', 'Пул 2 (WETH/DAI)']
    prices = [adjusted_price_1, adjusted_price_2]

    # Построение графика цен
    plt.figure(figsize=(10, 6))
    plt.bar(pools, prices, color=['blue', 'orange'])
    plt.xlabel('Пул')
    plt.ylabel('Цена WETH (USDT)')
    plt.title('Сравнение цен WETH в двух пулах')
    plt.show()

    # Построение графика разницы цен
    price_diff_percentage = abs(adjusted_price_1 - adjusted_price_2) / ((adjusted_price_1 + adjusted_price_2) / 2) * 100

    plt.figure(figsize=(10, 6))
    plt.bar(['Разница в цене'], [price_diff_percentage], color='green')
    plt.ylabel('Процентное изменение')
    plt.title('Разница в цене между пулами')
    plt.show()