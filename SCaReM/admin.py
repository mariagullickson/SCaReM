from django.contrib import admin
from django import forms
from .models import Resource, Tag, Camp


class ColorWidget(forms.RadioSelect):
    def render(self, name, value, attrs=None):
        # look up the colors that are already in use, and don't show them
        # unless they are in use by this camp
        camps = Camp.objects.all()
        camp_colors = [c.color for c in camps]
        choices = [x for x in self.choices
                   if x[0] == value or x[0] not in camp_colors]

        # render the options
        options = []
        for i, choice in enumerate(choices):
            choice_value, choice_label = choice
            if not choice_value:
                continue
            id = "id_%s_%s" % (name, i)
            checked = ''
            if choice_value == value:
                checked = 'checked="checked"'
            options.append(
                '<li><input id="%s" name="%s" %s '
                'type="radio" value="%s"/><span><div class="color-choice" '
                'style="background-color:%s"/></span></li>'
                % (id, name, checked, choice_value, choice_value))
        return '<ul id="id_%s">%s</ul>' \
            % (name, "\n".join(options))


class CampAdminForm(forms.ModelForm):
    class Meta:
        model = Camp
        fields = ['name', 'color']
        widgets = {
            'color': ColorWidget(),
            }


# we need to customize the camp admin, so we can have a nice
# color selector
class CampAdmin(admin.ModelAdmin):
    form = CampAdminForm

    class Media:
        css = {
            'all': ('css/camp_admin.css', )
            }


admin.site.register(Camp, CampAdmin)
admin.site.register(Resource)
admin.site.register(Tag)
