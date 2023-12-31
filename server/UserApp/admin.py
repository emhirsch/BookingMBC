from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, MBCGroup
from CalendarApp.models import Machine


import pandas as pd
import re
import io

from django.urls import path
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.db import IntegrityError
from django.db import transaction




@transaction.atomic
def clear_machines_for_all_users():
    # Fetch all UserProfile objects
    user_profiles = UserProfile.objects.all()

    # Loop through UserProfile objects
    for user_profile in user_profiles:
        # Clear the related machines4ThisUser queryset
        user_profile.machines4ThisUser.clear()


class UserExcelImportForm(forms.Form):
    excel_upload = forms.FileField()


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_group_name', 'is_external')  # Display these fields in the admin list view
    list_filter = ('group__group_name', 'is_external')  # Add a filter for group_name
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'group__group_name']  # Add this line to enable search by username

    def get_group_name(self, obj):
        return obj.group.group_name if obj.group else ''

    get_group_name.short_description = 'Group Name'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'machines4ThisUser':
            kwargs['queryset'] = db_field.remote_field.model.objects.order_by('machine_name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        new_urls1 = [path('upload-excel/', self.upload_excel),]
        new_urls2 = [path('download-excel/', self.download_excel),]
        return new_urls1 + new_urls2 + urls

    def upload_excel(self, request):
        if request.method == "POST":
            excel_file = request.FILES.get("excel_upload")
            # Call the function to clear machines4ThisUser for all users
            clear_machines_for_all_users()

            if not excel_file.name.endswith(('.xls', '.xlsx')):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)

            try:
                # Read the Excel file into a DataFrame
                df = pd.read_excel(excel_file)

                df=df.astype(object)
                df.fillna('', inplace=True) #fill first with a float64 compatible datatype 
                
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
                
                # Iterate over columns using iteritems
                for mn in df.columns:
                    #print(f"Machine: {mn}")
                    
                    # Iterate over rows for each column
                    for s in df[mn]:
                        # Use re.search to find the first email address in the input string
                        match = re.search(email_pattern, s)
                        
                        # If a match is found, return the extracted email address; otherwise, return None
                        ema = match.group() if match else ""
                        if ema == "": continue
                        #print(f"  User email: {ema}")
                        try:
                            usp=UserProfile.objects.get(user__email=ema)
                            m=Machine.objects.get(machine_name=mn)
                            usp.machines4ThisUser.add(m)
                            usp.save()
                        except UserProfile.DoesNotExist:
                            print(f"  email: {ema} not registered")
                            continue
                        except Machine.DoesNotExist:
                            print(f"  machine: {mn} not existent")
                            continue                            
                        except IntegrityError as e:
                            print(f"Error {e} processing email: {ema}")

                messages.success(request, 'Excel file uploaded successfully')
                return HttpResponseRedirect(request.path_info)

            except Exception as e:
                messages.error(request, f'Error processing the Excel file: {e}')
                return HttpResponseRedirect(request.path_info)

        form = UserExcelImportForm()  # Assume you have a form for file uploads
        data = {"form": form}
        return render(request, "admin/excel_upload.html", data)


    def download_excel(self, request):
        # Create an empty DataFrame
        machine_email_dict={}
        
        # Fetch all UserProfile objects
        user_profiles = UserProfile.objects.all()
    
        # Loop through UserProfile objects
        for user_profile in user_profiles:
            # Extract email from user
            email = user_profile.user.email
            # Extract the names of the machines listed in the ManyToMany relation
            machines_list = [machine.machine_name for machine in user_profile.machines4ThisUser.all()]
            #loop through these machine names
            for machine_name in machines_list:
                if machine_name not in machine_email_dict:
                    #create a new column if machine_name column not yet generated
                    machine_email_dict[machine_name] = []
                machine_email_dict[machine_name].append(email)    
        # Find the maximum number of values for any key
        max_values = max(len(values) for values in machine_email_dict.values())

        # Normalize the number of values for each key otherwise pandas dataframe will not work
        for key, values in machine_email_dict.items():
            # Pad the list with None to match the maximum number of values
            machine_email_dict[key] += ["None"] * (max_values - len(values))

        data = pd.DataFrame(machine_email_dict)

        # Create Excel file in memory
        excel_file = io.BytesIO()

        # Use ExcelWriter to set column widths
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            data.to_excel(writer, sheet_name='Machines', index=False)

            # Access the XlsxWriter worksheet object
            worksheet = writer.sheets['Machines']

            # Iterate through each column and set the width based on the maximum length of the column data
            for i, col in enumerate(data.columns):
                max_len = max(data[col].astype(str).apply(len).max(), len(col))
                worksheet.set_column(i, i, max_len + 2)  # Add a little extra space

        excel_file.seek(0)

        # Prepare response for download
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=machines4users.xlsx'
        response.write(excel_file.read())

        return response

            




class InitialLetterFilter(admin.SimpleListFilter):
    title = _('Initial Letter')
    parameter_name = 'initial'

    def lookups(self, request, model_admin):
        # Get the distinct initial letters in the group names
        group_names = MBCGroup.objects.values_list('group_name', flat=True)
        initial_letters = set(name[0].upper() for name in group_names if name)
        return [(letter, letter) for letter in sorted(initial_letters)]

    def queryset(self, request, queryset):
        if self.value():
            # Filter groups based on the selected initial letter
            return queryset.filter(group_name__startswith=self.value())
        return queryset


class MBCGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'location')
    list_filter = (InitialLetterFilter, 'location') #add list filters
    search_fields = ['group_name']  # Add this line to enable search by username
    ordering = ['group_name']  # Add ordering by group_name

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        # Check if the response is an instance of TemplateResponse
        if isinstance(response, TemplateResponse):
            # Add a custom context variable to display unique group names
            response.context_data['locations'] = MBCGroup.objects.values_list('location', flat=True).distinct()
        
        return response
        
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'machines_bought':
            kwargs['queryset'] = db_field.remote_field.model.objects.order_by('machine_name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(MBCGroup, MBCGroupAdmin)
