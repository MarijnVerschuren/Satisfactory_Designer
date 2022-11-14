import json
import sys
import os



# constants
levels = {
	"mk1": 0,
	"mk2": 1,
	"mk3": 2,
	"mk4": 3,
	"mk5": 4,
}

belt_levels = {
	levels["mk1"]: 60,
	levels["mk2"]: 120,
	levels["mk3"]: 270,
	levels["mk4"]: 480,
	levels["mk5"]: 780,
}
overclock_levels = [1, 1.5, 2, 2.5]
mining_levels = {
	levels["mk1"]: {"inpure": 30, "normal": 60, "pure": 120},
	levels["mk2"]: {"inpure": 60, "normal": 120, "pure": 240},
	levels["mk3"]: {"inpure": 120, "normal": 240, "pure": 480}
}

machines = [
	"smelter",
	"foundry",

	"constructor",
	"assembler"
]

# classs
class item:
	item_count = 0;
	def __init__(self, name):
		self.name = name
		self.id = item.item_count
		item.item_count += 1

	def __str__(self):	return f"{{id: {self.id}, name: {self.name}}}"
	def __repr__(self):	return str(self)

class ore(item):
	def __init__(self, name):
		super(ore, self).__init__(name)

class recipe(item):
	def __init__(self, name, machine, time, *items, output = 1):
		super(recipe, self).__init__(name)
		self.machine =		machine
		self.time =			time
		self.items =		items
		self.output =		output

	@property
	def native_per_min(self) -> int:	return self.output * (60 / self.time) 

	def __str__(self):					return f"{{id: {self.id}, name: {self.name}, machine: {self.machine}, time: {self.time}, items: {self.items}, output: {self.output}}}"

class item_encoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, recipe):
			return {"id": obj.id, "name": obj.name, "machine": obj.machine, "time": obj.time, "items": obj.items, "output": obj.output}
		if isinstance(obj, item) or isinstance(obj, ore):
			return {"id": obj.id, "name": obj.name}
		return json.JSONEncoder.default(self, obj)


# vars
mining_options = {}
item_list = []


# functions
clear_console =			lambda: os.system("cls" if os.name in ["nt", "dos"] else "clear")
filter_items_by_name =	lambda val: [x for x in item_list if x.name == val]


def get_item_tree(item_name: str, per_min: int = 0) -> list or int:
	recipes = filter_items_by_name(item_name)
	if len(recipes) > 1:
		for index, recipe in enumerate(recipes): print(f"({index}): {recipe}")
		choice = None
		while (not choice):
			try: choice = recipes[int(input("recipe: "))]
			except Exception as e:
				if e == KeyboardInterrupt: exit(0);
	else: choice = recipes[0]

	if isinstance(choice, ore): return (per_min, choice)  # f"{per_min} x {choice.name}"

	if not per_min:
		while True:
			try: per_min = int(input(f"items per minute (native: {choice.native_per_min}): ")) / choice.output; break
			except Exception as e:
				if e == KeyboardInterrupt: exit(0);
				sys.stdout.write("\033[F\033[K")
	else: per_min /= choice.output

	return [(per_min * choice.output, choice), [get_item_tree(item[0], per_min * item[1]) for item in choice.items]]  # f"{per_min / choice.native_per_min} x {choice.name}"


def print_item_tree(tree: list or str, indent: int = 0) -> None:
	for layer in tree:
		if isinstance(layer, tuple):
			per_min, obj = layer
			msg = " " * indent + obj.name
			if isinstance(obj, recipe):	msg += " " * (50 - len(msg)) + f"<overclock: {per_min / obj.native_per_min}, per_min: {per_min}>"
			else:						msg += " " * (50 - len(msg)) + f"<per_min: {per_min}>"
			print(msg); continue
		print_item_tree(layer, indent + 2)




if __name__ == "__main__":
	with open("recipe.json", "r") as file:
		recipe_params = json.load(file)

	with open("constraints.json", "r") as file:
		constraints = json.load(file)

	# calculat mining options based on constraints
	for oc in overclock_levels:
		for key, val in mining_levels.items():
			if key > constraints["mining_level"]: break
			for _key, _val in val.items():
				prod = round(min(belt_levels[constraints["belt_level"]], oc * _val))
				if prod not in mining_options: mining_options.update({prod: []})
				mining_options[prod].append({"mining_level": key, "purity": _key, "overclock": oc * 100})
	#print(json.dumps(mining_options, indent=4))

	for key, val in recipe_params.items():
		if not val: item_list.append(ore(key)); continue
		item_list.extend([recipe(key, *args, **kwargs) for args, kwargs in val])
	#print(json.dumps(item_list, cls=item_encoder, indent=4))

	clear_console()
	while True:
		item_name = input("item: "); sys.stdout.write("\033[F\033[K")
		if not item_name or not filter_items_by_name(item_name): input("item does not exist (press enter to continue)"); sys.stdout.write("\033[F\033[K"); continue
		
		tree = get_item_tree(item_name)
		print("\n\n")
		print_item_tree(tree)
		print("\n\n")