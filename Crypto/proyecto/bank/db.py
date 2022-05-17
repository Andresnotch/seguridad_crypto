import json, os.path as path


class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class DB(metaclass=Singleton):
	__internaldb__ = None

	@property
	def inner(self):
		if self.__internaldb__ is None:
			self.__internaldb__ = self.__load_db__()
		return self.__internaldb__

	def __load_db__(self) -> dict:
		if not path.exists('db.json'):
			with open('db.json', 'w') as f:
				json.dump(
					{
						'clients': {},
						'logs': {}
					},
					f,
				)
		with open('db.json', 'r') as f:
			return json.load(f)

	def save_db(self) -> None:
		with open('db.json', 'w') as f:
			json.dump(self.inner, f)
