from django.forms import ModelMultipleChoiceField


class FullNameContributorField(ModelMultipleChoiceField):
    def label_from_instance(self, user):
        return user.get_full_name() or user.get_username()
