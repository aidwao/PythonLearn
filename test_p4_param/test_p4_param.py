import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("arguments", type=str, nargs='*', help="All Arguments")
	args = parser.parse_args()
	arguments = args.arguments
	print(f"{arguments=}")