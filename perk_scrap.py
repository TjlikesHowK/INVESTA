import yfinance as yf

crypts = {
	'BTC-USD': ["btc-usd", "btc/usd", "btcusd", "btc", "bitcoin"],
	'ETH-USD': ["eth-usd", "eth/usd", "ethusd", "eth", "ethereum"],
	'BNB-USD': ["bnb-usd", "bnb/usd", "bnbusd", "bnb", "binancecoin"],
	'ADA-USD': ["ada-usd", "ada/usd", "adausd", "ada", "cardano"],
	'XRP-USD': ["xrp-usd", "xrp/usd", "xrpusd", "xrp", "xrp"],
	'HEX-USD': ["hex-usd", "hex/usd", "hexusd", "hex", "hex"],
	'LTC-USD': ["ltc-usd", "ltc/usd", "ltcusd", "ltc", "litecoin"],
	'BCH-USD': ["bch-usd", "bch/usd", "bchusd", "bch", "bitcoincash"],
	'VET-USD': ["vet-usd", "vet/usd", "vetusd", "vet", "vechain"],
	'XLM-USD': ["xlm-usd", "xlm/usd", "xlmusd", "xlm", "stellar"],
	'AXS-USD': ["axs-usd", "axs/usd", "axsusd", "axs", "axieinfinity"],
	'CRO-USD': ["cro-usd", "cro/usd", "crousd", "cro", "cryptocomcoin"],
	'USDT-USD': ["usdt-usd", "usdt/usd", "usdtusd", "usdt", "tether"],
	'SOL1-USD': ["sol1-usd", "sol1/usd", "sol1usd", "sol1", "solana"],
	'UNI3-USD': ["uni3-usd", "uni3/usd", "uni3usd", "uni3", "uniswap"],
	'LINK-USD': ["link-usd", "link/usd", "linkusd", "link", "chainlink"],
	'DOT1-USD': ["dot1-usd", "dot1/usd", "dot1usd", "dot1", "polkadot"],
	'DOGE-USD': ["doge-usd", "doge/usd", "dogeusd", "doge", "dogecoin"],
	'ICP1-USD': ["icp1-usd", "icp1/usd", "icp1usd", "icp1", "internetcomputer"],
	'USDC-USD': ["usdc-usd", "usdc/usd", "usdcusd", "usdc", "usdcoin"],
	'SHIB-USD': ["shib-usd", "shib/usd", "shibusd", "shib", "shiba inu"],
	'AVAX-USD': ["avax-usd", "avax/usd", "avaxusd", "avax", "avalanche"],
	'ALGO-USD': ["algo-usd", "algo/usd", "algousd", "algo", "algorand"],
	'LUNA1-USD': ["luna1-usd", "luna1/usd", "luna1usd", "luna1", "terra"],
	'MATIC-USD': ["matic-usd", "matic/usd", "maticusd", "matic", "maticnetwork"]
}

def driver(quotation):
	with open("ME.txt", "r") as f:
		for ticker in f:
			if ticker == f"{quotation}\n":
				quotation += ".ME"

	for crypt in crypts:
		for i in range(len(crypts[crypt])):
			if quotation.lower() == crypts[crypt][i]:
				quotation = crypt

	tick = yf.Ticker(quotation)

	currency = tick.info["currency"]
	
	try:
		current_price = tick.info["currentPrice"]
	except Exception as err:
		current_price = tick.info["regularMarketPrice"]

	try:
		open_price = tick.info["open"]
	except Exception as err:
		open_price = tick.info["regularMarketOpen"]

	d1 = round(float(current_price) - float(open_price), 10)
	d2 = round(((float(current_price) * 100) / float(open_price)) - 100, 10)
	change_per_day = f"{d1}({d2}%)".replace("e-", "+").replace("-", "−").replace("+", "e-")

	return current_price, change_per_day, currency