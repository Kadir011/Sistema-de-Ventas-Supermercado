"""
Templates para la página de "Legal" y "Privacy Policy".
"""

from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    template_name = 'super/legal/privacy_policy.html'


class TermsOfServiceView(TemplateView):
    template_name = 'super/legal/terms_of_service.html'


class DataDeletionView(TemplateView):
    template_name = 'super/legal/data_deletion.html'
