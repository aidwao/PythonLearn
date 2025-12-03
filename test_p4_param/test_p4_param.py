import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("changelist", type=str, help="Changelist number")
	args = parser.parse_args()
	changelist_num = args.changelist
	print(f" param = {changelist_num} ")