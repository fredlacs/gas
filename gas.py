#!/usr/bin/env python3

# pip3 install web3


import requests, json
from decimal import Decimal
from web3 import Web3

acc = []

skip = 0
size = 5
infura_key=""

if not size > 0 or size > 100:
    print("Size should be 0 < size <= 100")
    exit()


if infura_key == "":
    print("Set your infura key")
    exit()


# Tuesday, 22 September 2020 23:00:00
earliest = 1600815600
# 6 hours ago
earliest = 1608738208

try:
    while True:
        query = """{
        swaps(
            orderBy: timestamp,
            orderDirection: desc,
            first: """+str(size)+""",
            skip:"""+ str(skip)+"""
            where: {
                timestamp_gte: """+str(earliest)+"""
            }
        ) {
            timestamp
            transaction {
                id
            }
        }
        }
        """
        url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
        r = requests.post(url, json={'query': query})
        json_data = json.loads(r.text)["data"]["swaps"]
        
        print("got " + str(len(json_data)) + " txs ")
        print("timestamp " + json_data[0]["timestamp"])
        # (hash, timestamp)
        txs = [(entry["transaction"]["id"], entry["timestamp"]) for entry in json_data]



        w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/'+infura_key))

        # (tx, timestamp)
        txs = [ (w3.eth.getTransaction(foo[0]),w3.eth.getTransactionReceipt(foo[0]), foo[1]) for foo in txs]

        txs = [(tx[0]["gasPrice"],tx[1]["gasUsed"], tx[2]) for tx in txs]

        paid_in_usd = []
        for (price_per_gas, gas_used, time) in txs:
            url = "https://min-api.cryptocompare.com/data/v2/histohour?fsym=ETH&tsym=USD&limit=1&toTs=" + str(time)
            r = requests.get(url)
            price_data = json.loads(r.text)
            prices = price_data["Data"]["Data"]
            avg_eth_price = sum(d['high'] for d in prices) / len(prices)

            wei_paid = gas_used * price_per_gas
            total_paid_ether = Web3.fromWei(wei_paid, "ether")

            print("price " + str(total_paid_ether) + " eth")
            price_in_usd = total_paid_ether * Decimal(avg_eth_price)
            print("price paid $" + str(price_in_usd))
            paid_in_usd.append(price_in_usd)
        
        avg_price = sum(paid_in_usd) / len(paid_in_usd)
        print("Average paid $" + str(avg_price))


        acc.extend(txs)
        # skip += 100
        break
except KeyError as err:
    print(err)


# print(acc)
# print(len(acc))
