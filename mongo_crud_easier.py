from pymongo import MongoClient

class MongoCrudEasier:
	def __init__(self):
		self.client = MongoClient('localhost:27017')
		self.db = self.client.TODO

	def create(self, id, title, desc, done):
		try:
			self.db.list.insert_one({"id": id, "title": title, "description": desc, "done": done})
		except Exception as e:
			print(str(e))

	def remove(self, id):
		try:
			self.db.list.delete_many({"id": id})
		except Exception as e:
			print (str(e))

	def update(self, id, title, desc, done):
		try:
			self.db.list.update_one({"id": id},
							  		{"$set": {"title": title, "description": desc, "done": done}})
		except Exception as e:
			print (str(e))

	def read(self):
		return self.db.list.find()

	def next_entry_id(self):
		res = self.db.list.find_one(sort=[("id", -1)])
		if res is not None:
			return res['id'] + 1
		return 0
