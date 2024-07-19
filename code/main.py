import os

from web3 import Web3
import matplotlib.pyplot as plt
from plot import make_plot
from slippage import slippage
from gas import check_gas
from dotenv import load_dotenv

load_dotenv()

your_token = os.getenv("YOUR_TOKEN")

# Подключение к узлу Ethereum
infura_url = f'https://mainnet.infura.io/v3/{your_token}'
web3 = Web3(Web3.HTTPProvider(infura_url))

if not web3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum node")

# Адрес контракта Uniswap V2 Factory
factory_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'

# ABI для Uniswap V2 Factory
factory_abi = [
    {
        "constant": True,
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"}
        ],
        "name": "getPair",
        "outputs": [
            {"internalType": "address", "name": "pair", "type": "address"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# Адреса токенов WETH, USDT и DAI
weth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
usdt_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
dai_address = '0x6B175474E89094C44Da98b954EedeAC495271d0F'  # Например, DAI

# Создание контракта Factory
factory = web3.eth.contract(address=factory_address, abi=factory_abi)

# Получение адресов двух пулов
# Пул 1: WETH/USDT
pool_1_address = factory.functions.getPair(weth_address, usdt_address).call()
# Пул 2: WETH/DAI
pool_2_address = factory.functions.getPair(weth_address, dai_address).call()

if pool_1_address == '0x0000000000000000000000000000000000000000' or pool_2_address == '0x0000000000000000000000000000000000000000':
    raise ValueError("One of the pairs does not exist in Uniswap V2")

# ABI для Uniswap V2 Pair
pair_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# Создание контрактных объектов для каждого пула
pool_1 = web3.eth.contract(address=pool_1_address, abi=pair_abi)
pool_2 = web3.eth.contract(address=pool_2_address, abi=pair_abi)

# Получение резервов для каждого пула
reserves_1 = pool_1.functions.getReserves().call()
reserves_2 = pool_2.functions.getReserves().call()


def get_normalized_reserves(reserves, token0, token1, token0_decimals, token1_decimals):
    reserve0 = reserves[0] / (10 ** token0_decimals)
    reserve1 = reserves[1] / (10 ** token1_decimals)
    if token0.lower() < token1.lower():
        return reserve0, reserve1
    else:
        return reserve1, reserve0


eth_reserve_1, usdt_reserve_1 = get_normalized_reserves(reserves_1, weth_address, usdt_address, 18, 6)
eth_reserve_2, dai_reserve_2 = get_normalized_reserves(reserves_2, weth_address, dai_address, 18, 18)

# Корректный расчет цены для пары WETH/USDT и WETH/DAI
price_1 = usdt_reserve_1 / eth_reserve_1
price_2 = dai_reserve_2 / eth_reserve_2

# Конвертация цены DAI в USDT (считаем, что 1 DAI = 1 USDT)
price_2_in_usdt = price_2  # В реальности может потребоваться получение курса обмена DAI/USDT

# Стоимость газа в USDT
gas_cost_usdt = check_gas(web3) * price_1  # Конвертируем в USDT по цене из пула 1

price_diff_percentage, slip1, slip2 = slippage(price_1, price_2_in_usdt, usdt_reserve_1, eth_reserve_1,
                                               eth_reserve_2, dai_reserve_2)



# Пример данных для визуализации
pools = ['Пул 1 (WETH/USDT)', 'Пул 2 (WETH/DAI)']
prices = [price_1, price_2_in_usdt]
slippages = [slip1, slip2]

# Построение графика цен
plt.figure(figsize=(14, 7))

plt.subplot(1, 2, 1)
plt.bar(pools, prices, color=['blue', 'orange'])
plt.xlabel('Пул')
plt.ylabel('Цена WETH (USDT)')
plt.title('Цены WETH в разных пулах')

# Построение графика проскальзывания
plt.subplot(1, 2, 2)
plt.bar(pools, slippages, color=['blue', 'orange'])
plt.xlabel('Пул')
plt.ylabel('Проскальзывание (%)')
plt.title('Проскальзывание в пулах')

plt.tight_layout()
# plt.show()

# Построение графика разницы в цене
plt.figure(figsize=(7, 5))
plt.bar(['Разница в цене'], [price_diff_percentage], color='green')
plt.ylabel('Процентное изменение')
plt.title('Разница в цене между пулами')
# plt.show()

plt.savefig('plot.png')


# Вывод результатов
print(f"Адрес пула 1 (WETH/USDT): {pool_1_address}")
print(f"Адрес пула 2 (WETH/DAI): {pool_2_address}")
print(f"Цена WETH в пуле 1: {price_1:.6f} USDT")
print(f"Цена WETH в пуле 2: {price_2_in_usdt:.6f} USDT")
print(f"Разница в цене: {price_diff_percentage:.2f}%")


if price_diff_percentage > 0.5:
    potential_profit = (price_1 - price_2_in_usdt) - gas_cost_usdt
    if potential_profit > 0:
        print("Возможна арбитражная возможность с учетом газовых расходов!")
    else:
        print("Арбитражная возможность отсутствует из-за газовых расходов.")
else:
    print("Арбитражная возможность отсутствует.")
