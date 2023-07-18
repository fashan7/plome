from django.shortcuts import render
from accounts.models import CustomUserTypes
from pagesallocation.models import PageAllocation,Privilege
from django.http import JsonResponse

from django.db.models import OuterRef, Subquery
from django.db.models import Q, F

# Create your views here.
def setup_privilege(request):

    user = CustomUserTypes.objects.all()
    return render(request,'base/set_priviledge.html',  {'users': user})




def get_primary_section():
    items = dict()
    queryset = PageAllocation.objects.filter(is_active=True).values('psection').distinct()
    psection_list = queryset.values_list('psection', flat=True)
    for x, row in enumerate(psection_list, start=1):
        items.update({x: row})
    return items

def get_new_pages_not_set(section):
    # Subquery to get the pageallocation_id values in the Userpriviledge (Privilege) table
    subquery = Privilege.objects.filter(pageallocation_id=OuterRef('id')).values('pageallocation_id')   

    # Query to get the Pageallocation items where there is no corresponding Userpriviledge (Privilege) entry
    # and other filtering conditions
    items = PageAllocation.objects.filter(
        psection=section,
        is_active=True,
        privileges__pageallocation_id__isnull=True
    ).exclude(
        id__in=Subquery(subquery)
    ).values('name', 'route', 'id')


    if items is not None:
        data = list()
        for row in items:
            data.append({'name': row[0], 'route': row[1], 'page_id': row[2]})
        return data
    else:
        return None
    
def get_priv_pages(section, user_id):
    privileges = Privilege.objects.filter(
        Q(pageallocation__psection=section) &
        Q(pageallocation__is_active=True) &
        Q(assigned_users=user_id)
    ).order_by(F('pageallocation__pposition'))

    return privileges.values(
        'pageallocation__name',
        'is_active',
        'id'
    )


def process_load_privledge(user_id):
    pages = get_primary_section()
    for key, value in pages.items():
        section_name = value
        data_not_set = get_new_pages_not_set(section_name)
        if data_not_set:
            for row in data_not_set:
                page_id = row.get('page_id')
                register_privledges(page_id)

    form_dict = dict()
    for key, value in pages.items():
        section_name = value
        data = get_priv_pages(section_name, user_id)
        form_dict.update({section_name: data})
    return form_dict





def register_privledges(page_id):
    #todo need to check status is_active
    for user in CustomUserTypes.objects.all():

        privilege = Privilege()
        privilege.pageallocation_id = page_id
        privilege.is_active = False
        privilege.assigned_users.set([user])

        privilege.save()


def get_page_priv(request):
    user = request.POST.get('user')
    a =process_load_privledge(user)
    print(a)
    return render(request,'base/loadprivPages.html')
