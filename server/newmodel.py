# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
# populate_database.py

import os
import sys
import pandas as pd
import django

from UserApp.models import UserProfile, MBCGroup
#from CalendarApp.models import Machine

def populate_xls(excel_filename):
    user_profiles = UserProfile.objects.all()
    
    # Create a list of dictionaries containing email and group_name
    data = [{'email': profile.user.email, 'group': profile.group_name} for profile in user_profiles]
    
    # Create a Pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(data)
    df.to_excel(excel_filename, index=False)
    print("Excel file created successfully.")



def populate_model(excel_filename):
    # Read Excel file into a DataFrame
    df = pd.read_excel(excel_filename)
    
    # Iterate through the DataFrame rows and update UserProfile instances
    for index, row in df.iterrows():
        email = row['email']
        gname = row['group']        
        try:
            # Find UserProfile based on email
            user_profile = UserProfile.objects.get(user__email=email)
    
            try:
                # Try to find MBCGroup based on group_name
                mbc_group = MBCGroup.objects.get(group_name=gname)
    
                # Update UserProfile's group field
                user_profile.group = mbc_group
    
                # Save the changes to the database
                user_profile.save()
    
            except MBCGroup.DoesNotExist:
                print(f"Error: MBCGroup with group_name '{gname}' not found.")   
        except UserProfile.DoesNotExist:
            print(f"Error: UserProfile with email '{email}' not found.")
    print("UserProfiles updated successfully.")
    

if __name__ == "__main__":
    # Set the Django project settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BookingMBC.settings")

    # Add the project root directory to the Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # Setup Django
    django.setup()

    if len(sys.argv) != 2:
        print("Usage: python script_name.py [2excel | 2model]")
        sys.exit(1)

    excel_filename = 'oldgroupsemail.xlsx'
    option = sys.argv[1]

    if option == "2excel":
        populate_xls(excel_filename)
    elif option == "2model":
        populate_model(excel_filename)
    else:
        print("Invalid option. Use '2excel' or '2model'.")
        sys.exit(1)    # Assuming the script is in the root directory of your project

