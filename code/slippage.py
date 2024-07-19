def slippage(price_1, price_2_in_usdt, usdt_reserve_1, eth_reserve_1, eth_reserve_2, dai_reserve_2):
    # Расчет проскальзывания
    slippage_tolerance = 0.005  # 0.5% проскальзывания, 0.005 в виде десятичного дроби

    # Определяем размер ордера (например, 1 ETH)
    order_size = 1  # 1 ETH

    slippage_1 = calculate_slippage(price_1, usdt_reserve_1, eth_reserve_1, order_size)
    slippage_2 = calculate_slippage(price_2_in_usdt, dai_reserve_2, eth_reserve_2, order_size)

    # Корректировка цен с учетом проскальзывания
    adjusted_price_1 = price_1 * (1 + slippage_tolerance)
    adjusted_price_2 = price_2_in_usdt * (1 - slippage_tolerance)

    # Разница в цене с учетом проскальзывания
    price_diff_percentage = abs(adjusted_price_1 - adjusted_price_2) / ((adjusted_price_1 + adjusted_price_2) / 2) * 100

    return price_diff_percentage, slippage_1, slippage_2


# Расчет проскальзывания на основе объема торговли
def calculate_slippage(price, reserve_token, reserve_base, amount):
    return (amount / (reserve_base + amount)) * (price / reserve_token)
