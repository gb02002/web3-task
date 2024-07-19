from web3 import Web3


def check_gas(web3: Web3):
    gas_price = web3.eth.gas_price  # в wei

    # Предполагаемое количество газа для арбитража
    gas_limit = 200000  # Это примерное значение, нужно уточнить для конкретной стратегии

    # Стоимость газа в ETH
    gas_cost_eth = gas_price * gas_limit / (10 ** 18)

    return gas_cost_eth