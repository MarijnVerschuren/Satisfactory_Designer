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

items = {
	"bauxite":						None,
	"caterium":						None,
	"coal":							None,
	"copper":						None,
	"iron":							None,
	"limestone":					None,
	"quartz":						None,
	"sam":							None,
	"sulfur":						None,
	"uranium":						None,

	"iron_bar":						[
		(("smelter", 2, ("iron", 1)), {})
	],
	"copper_bar":					[
		(("smelter", 2, ("copper", 1)), {}),
		(("foundry", 12, ("copper", 10), ("iron", 5)), {"output": 20})
	],
	"caterium_bar":					[
		(("smelter", 4, ("caterium", 1)), {})
	],
	"steel_bar":					[
		(("foundry", 4, ("iron", 3), ("coal", 3)), {"output": 3})
	],

	"iron_plate":					[
		(("constructor", 6, ("iron_bar", 3)), {"output": 2})
	],
	"iron_rod":						[
		(("constructor", 4, ("iron_bar", 1)), {})
	],
	"screw":						[
		(("constructor", 6, ("iron_rod", 1)), {"output": 4})
	],
	"copper_sheet":					[
		(("constructor", 6, ("copper_bar", 2)), {})
	],
	"steel_beam":					[
		(("constructor", 4, ("steel_bar", 4)), {})
	],
	"steel_pipe":					[
		(("constructor", 6, ("steel_bar", 3)), {"output": 2})
	],
	"wire":							[
		(("constructor", 4, ("copper_bar", 1)), {"output": 2})
	],
	"cable":						[
		(("constructor", 2, ("wire", 2)), {})
	],
	"quick_wire":					[
		(("constructor", 5, ("caterium_bar", 1)), {"output": 5})
	],
	"concrete":						[
		(("constructor", 4, ("limestone", 3)), {})
	],
	"quartz_crystal":				[
		(("constructor", 8, ("quartz", 5)), {"output": 3})
	],
	"silica":						[
		(("constructor", 8, ("quartz", 3)), {"output": 5})
	],

	"reinforced_iron_plate":		[
		(("assembler", 12, ("iron_plate", 6), ("screw", 12)), {})
	],
	"modular_frame":				[
		(("assembler", 60, ("reinforced_iron_plate", 3), ("iron_rod", 12)), {"output": 2}),
		(("assembler", 24, ("reinforced_iron_plate", 3), ("screw", 56)), {"output": 2})
	],
	"rotor":						[
		(("assembler", 15, ("iron_rod", 5), ("screw", 25)), {})
	],
}

# classs and functions
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
	def __init__(self, name, machine, time, *_items, output = 1):
		super(recipe, self).__init__(name)
		self.machine =		machine
		self.time =			time
		self.items =		_items
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
constraints = {
    "belt_level": levels["mk2"],
    "mining_level": levels["mk2"],
    "overclock_count": 6
}
mining_options = {}
item_list = []

if __name__ == "__main__":
	with open("recipe.json", "r") as file:
		json.load(file)

	with open("constraints.json", "r") as file:
		json.load(file)

	input('sadasd')

	# calculat mining options based on constraints
	for oc in overclock_levels:
		for key, val in mining_levels.items():
			if key > constraints["mining_level"]: break
			for _key, _val in val.items():
				prod = round(min(belt_levels[constraints["belt_level"]], oc * _val))
				if prod not in mining_options: mining_options.update({prod: []})
				mining_options[prod].append({"mining_level": key, "purity": _key, "overclock": oc * 100})

	print(json.dumps(mining_options, indent=4))

	for key, val in items.items():
		if not val: item_list.append(ore(key)); continue
		item_list.extend([recipe(key, *args, **kwargs) for args, kwargs in val])

	print(json.dumps(item_list, cls=item_encoder, indent=4))