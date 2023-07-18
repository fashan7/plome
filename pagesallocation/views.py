from django.shortcuts import render,get_object_or_404
from accounts.models import CustomUserTypes
from pagesallocation.models import PageAllocation,Privilege
from django.http import JsonResponse

from django.db.models import OuterRef, Subquery, Q, F,Count

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
    
    subquery = Privilege.objects.filter(pageallocation_id=OuterRef('pk')).values('pageallocation_id')
    pageallocations_with_privileges = PageAllocation.objects.annotate(privilege_count=Count(Subquery(subquery)))
    # Query to get the desired items using Django ORM
    items = pageallocations_with_privileges.filter(
        Q(psection=section) &
        Q(is_active=True) &
        Q(privilege_count=0)
    ).order_by('pposition').values(
        'name',
        'route',
        'id'
    )

    if items is not None:
        data = list()
        for row in items:
            data.append({'name': row['name'], 'route': row['route'], 'page_id': row['id']})
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
        print("****")
        print(data_not_set)
        if data_not_set:
            for row in data_not_set:
                page_id = row.get('page_id')
                print('OOSOS')
                print(page_id)
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
        
        try:
            page_allocation = PageAllocation.objects.get(id=page_id)
        except PageAllocation.DoesNotExist:
            # Handle the case when the PageAllocation with the given page_id does not exist
            return
        
        user = get_object_or_404(CustomUserTypes, id=user.id)
        privilege = Privilege.objects.create(pageallocation=page_allocation, is_active=True, assigned_users=user)

        privilege.save()


def get_page_priv(request):
    user = request.POST.get('user')
    a =process_load_privledge(user)
    print(a)
    return render(request,'base/loadprivPages.html')
