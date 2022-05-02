from sqlalchemy import func


class BaseAggregator:

    def __init__(self, project: list = None):
        self._resolved_fields = self.get_as_dict
        if project:
            self.resolved_fields = {}
            for field, aggr_expr in self._resolved_fields.items():
                if field in project:
                    self.resolved_fields[field] = aggr_expr
        else:
            self.resolved_fields = self._resolved_fields

    @property
    def get_resolved(self):
        return self.resolved_fields

    @property
    def get_as_dict(self):
        return vars(self)


__all__ = ["BaseAggregator", "func"]
