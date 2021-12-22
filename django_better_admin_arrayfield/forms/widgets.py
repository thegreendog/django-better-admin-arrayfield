import json

from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.dateparse import parse_datetime


class DynamicArrayWidget(forms.TextInput):

    template_name = "django_better_admin_arrayfield/forms/widgets/dynamic_array.html"

    def __init__(self, *args, **kwargs):
        self.subwidget_form = kwargs.pop("subwidget_form", forms.TextInput)
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context_value = value or [""]
        context = super().get_context(name, context_value, attrs)
        final_attrs = context["widget"]["attrs"]
        id_ = context["widget"]["attrs"].get("id")
        context["widget"]["is_none"] = value is None

        subwidgets = []
        for index, item in enumerate(context["widget"]["value"]):
            widget_attrs = final_attrs.copy()
            if id_:
                widget_attrs["id"] = "{id_}_{index}".format(id_=id_, index=index)
            widget = self.subwidget_form()
            widget.is_required = self.is_required
            subwidgets.append(widget.get_context(name, item, widget_attrs)["widget"])

        context["widget"]["subwidgets"] = subwidgets
        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
            return [value for value in getter(name) if value]
        except AttributeError:
            return data.get(name)

    def value_omitted_from_data(self, data, files, name):
        return False

    def format_value(self, value):
        return value or []


class DynamicArrayTextareaWidget(DynamicArrayWidget):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("subwidget_form", forms.Textarea)
        super().__init__(*args, **kwargs)

class DatetimeWidget(DynamicArrayWidget):
    """Widget for array datetime lists"""

    def __init__(self, *args, **kwargs):
        kwargs['subwidget_form'] = AdminSplitDateTime
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
            dates = getter(name + '_0')
            times = getter(name + '_1')
            return_data = []
            for i in range(len(dates)):
                if dates[i] and times[i]:
                    return_data.append(parse_datetime(
                        ' '.join([dates[i], times[i]])))
            return return_data
        except AttributeError:
            return data.get(name)

class JSONWidget(DynamicArrayWidget):
    """Widget for array JSON lists"""

    def format_value(self, value):
        return [data if isinstance(data, str) else json.dumps(data) for data in value] or []
