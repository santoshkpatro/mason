from mason.db.connection import Database

class MasonModel:
    _table_name = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Check Meta.table_name if defined
        meta = getattr(cls, "Meta", None)
        if meta and hasattr(meta, "table_name"):
            cls._table_name = meta.table_name
        else:
            cls._table_name = MasonModel._infer_table_name(cls.__name__)

    @staticmethod
    def _infer_table_name(class_name):
        name = class_name.lower()
        if name.endswith("y"):
            return name[:-1] + "ies"
        elif name.endswith("s"):
            return name + "es"
        else:
            return name + "s"

    @classmethod
    def _get_table_name(cls):
        return cls._table_name

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={getattr(self, 'id', 'N/A')}>"

    @classmethod
    def all(cls):
        cursor = Database.execute(f"SELECT * FROM {cls._get_table_name()}")
        rows = cursor.fetchall()
        return [cls(**dict(row)) for row in rows]

    @classmethod
    def find(cls, id):
        cursor = Database.execute(f"SELECT * FROM {cls._get_table_name()} WHERE id = ?", (id,))
        row = cursor.fetchone()
        return cls(**dict(row)) if row else None

    @classmethod
    def find_by(cls, **kwargs):
        conditions = " AND ".join(f"{k} = ?" for k in kwargs.keys())
        values = tuple(kwargs.values())
        cursor = Database.execute(f"SELECT * FROM {cls._get_table_name()} WHERE {conditions}", values)
        rows = cursor.fetchall()
        return [cls(**dict(row)) for row in rows] if rows else []

    def update(self, **update_data):
        if not hasattr(self, 'id'):
            raise ValueError("Cannot update a model without an ID")

        fields = [f"{k} = ?" for k in update_data.keys() if k != "id"]
        values = [v for k, v in update_data.items() if k != "id"]

        update_query = f"UPDATE {self._get_table_name()} SET {', '.join(fields)} WHERE id = ?"
        Database.execute(update_query, (*values, self.id))

        # Update current object
        for k, v in update_data.items():
            if k != "id":
                setattr(self, k, v)

    def _perform_insert(self):
        data = self.__dict__.copy()
        keys = list(data.keys())
        placeholders = ", ".join(["?"] * len(keys))
        values = [data[k] for k in keys]
        insert_query = f"INSERT INTO {self._get_table_name()} ({', '.join(keys)}) VALUES ({placeholders})"
        cursor = Database.execute(insert_query, values)
        self.id = cursor.lastrowid  # Set the ID of the newly created object


    def save(self):
        if getattr(self, "id", None):
            self.update(**self.__dict__)
        else:
            self._perform_insert()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance