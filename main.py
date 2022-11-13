import json
import sys



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

	def __str__(self):	return f"{{id: {self.id}, name: {self.name}, machine: {self.machine}, time: {self.time}, items: {self.items}, output: {self.output}}}"

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
filter_items_by_name =	lambda val: [x for x in item_list if x.name == val]
def get_item_tree(item_name: str, per_min: int = 0) -> list:
	recipes = filter_items_by_name(item_name)
	if len(recipes) > 1:
		for index, recipe in enumerate(recipes): print(f"({index}): {recipe}")
		choice = None
		while (not choice):
			try: choice = recipes[int(input("recipe: "))]
			except: pass
	else: choice = recipes[0]

	if isinstance(choice, ore): return f"{per_min} x {choice.name}"

	if not per_min:	per_min = (60 / choice.time)
	else:			per_min /= choice.output

	return [f"{per_min} x {choice.name}", [get_item_tree(item[0], per_min * item[1]) for item in choice.items]]

def print_item_tree(tree: list or str) -> None:
	for layer in tree:
		if isinstance(layer, str): print(layer); continue
		print_item_tree(layer)



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

	print_item_tree(get_item_tree("modular_frame"))