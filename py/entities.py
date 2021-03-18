from collections.abc import Mapping


class Entities(Mapping):
    def __init__(self, app, *args, **kw):
        self._storage = dict(*args, **kw)
        #   self.ent_count = ent_count
        self.app = app

    def __getitem__(self, key):
        self.update_count()
        return self._storage[key]

    def __iter__(self):
        self.update_count()
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    #   def __delitem__(self, key):
    #      return self._storage.__delitem__(self, key)

    def add_item(self, key, value):
        ret = self._storage[key].append(value)
        self.update_count()
        return ret

    def __setitem__(self, key, value):
        ret = self._storage.__setitem__(key, value)
        self.update_count()
        return ret

    def update_count(self):
        self.app.ent_count = "\n".join(
            [
                "{}={}".format(key, len(val))
                for key, val in self._storage.items()
            ]
        )

    def __str__(self):
        self.update_count()
        return self._storage.__str__()
