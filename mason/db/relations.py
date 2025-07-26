import importlib


class ForeignKey:
    def __init__(self, model_name, through, field="id"):
        """
        model_name: Name of the related model (e.g., "User")
        through: The foreign key column name in this model (e.g., "user_id")
        field: The related model's primary key field (default = "id")
        """
        self.model_name = model_name
        self.through = through
        self.field = field
        self._model_class = None

    def _get_model_class(self):
        if self._model_class:
            return self._model_class

        module_path = f"app.models.{self.model_name.lower()}"
        module = importlib.import_module(module_path)
        self._model_class = getattr(module, self.model_name)
        return self._model_class

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = getattr(instance, self.through, None)
        if value is None:
            return None

        model_class = self._get_model_class()
        return model_class.find(value)


class RelatedSet:
    def __init__(self, model_name, through):
        """
        model_name: Name of the related model (string)
        through: Column in the related model that refers to this model's ID
        """
        self.model_name = model_name
        self.through = through
        self._model_class = None

    def _get_model_class(self):
        if self._model_class:
            return self._model_class

        module_path = f"app.models.{self.model_name.lower()}"
        module = importlib.import_module(module_path)
        self._model_class = getattr(module, self.model_name)
        return self._model_class

    def __get__(self, instance, owner):
        if instance is None:
            return self
        model_class = self._get_model_class()
        return model_class.find_by(**{self.through: instance.id})