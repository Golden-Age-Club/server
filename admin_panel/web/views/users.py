from django.views.generic import TemplateView, FormView, View
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from repository.users import UserRepository
from audit.decorators import log_action
from web.forms import UserEditForm

class UserListView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/user_list.html'

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        search = self.request.GET.get('q', '')
        
        context.update(UserRepository.get_users(page=page, search=search))
        context['search_query'] = search
        context['app_label'] = 'web'
        context['model_name'] = 'management'
        context.update(admin.site.each_context(self.request))
        return context

class UserUpdateView(LoginRequiredMixin, FormView):
    template_name = 'admin/user_form.html'
    form_class = UserEditForm

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        user_id = self.kwargs['pk']
        user = UserRepository.get_user_by_id(user_id)
        if user:
            context['mongo_user'] = user
        context['app_label'] = 'web'
        context['model_name'] = 'management'
        context.update(admin.site.each_context(self.request))
        return context

    def get_initial(self):
        user_id = self.kwargs['pk']
        user = UserRepository.get_user_by_id(user_id)
        if user:
            return {
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "is_active": user.get("is_active", True),
                "is_premium": user.get("is_premium", False),
                "balance": user.get("balance", 0.0),
            }
        return {}

    @log_action(action_type='UPDATE', collection_name='users')
    def form_valid(self, form):
        user_id = self.kwargs['pk']
        data = form.cleaned_data
        
        # Only admins can update balance, check permission if implementing finer grain
        # user = self.request.user
        
        success = UserRepository.update_user(user_id, data)
        if success:
            messages.success(self.request, f"User {user_id} updated successfully.")
        else:
            messages.error(self.request, "Failed to update user.")
            
        return redirect('web:user_list')

class UserToggleStatusView(LoginRequiredMixin, View):
    @log_action(action_type='DISABLE_ENABLE', collection_name='users')
    def post(self, request, pk):
        user = UserRepository.get_user_by_id(pk)
        if user:
            current_status = user.get("is_active", True)
            UserRepository.update_user(pk, {"is_active": not current_status})
            messages.success(request, f"User status toggled.")
        return redirect('web:user_list')
