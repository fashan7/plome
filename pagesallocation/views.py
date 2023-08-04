from django.shortcuts import render,get_object_or_404
from accounts.models import CustomUserTypes
from pagesallocation.models import PageAllocation,Privilege
from django.http import JsonResponse

from django.db.models import OuterRef, Subquery, Q, F,Count

# Create your views here.
def setup_privilege(request):
    if not request.user.is_authenticated:
        return render(request, 'accounts/auth-login.html')
        
    
    user_auth = request.user
    nav_data = navigation_data(user_auth.id)
    
    user = CustomUserTypes.objects.all()
    return render(request,'base/set_priviledge.html',  {'users': user, 'sections' : nav_data})


def group_sections(user_id):
    pages_sections = PageAllocation.objects.filter(
        is_active=True,
        privileges__is_active=True,
        privileges__assigned_users_id=user_id
    ).annotate(countP=Count('id')).order_by('psection')

    if pages_sections:
        data = [{
            'psection': page_section.psection,
            'count': pages_sections.filter(psection=page_section).count(),
        } for page_section in pages_sections]
        return data
    else:
        return None
    
def get_sub_sections(user_id, section_id):
    subsections = Privilege.objects.filter(
        pageallocation__psection=section_id,
        pageallocation__is_active=True,
        assigned_users_id=user_id
    ).order_by('pageallocation__sposition').values(
        'pageallocation__name',
        'is_active',
        'id',
        'pageallocation__route'
    )
    
    if subsections:
        data = [{
            'sub_section_name': subsection.get('pageallocation__name'),
            'is_active': subsection.get('is_active'),
            'priv_id': subsection.get('id'), 
            'route': subsection.get('pageallocation__route'),
        } for subsection in subsections]
        return data
    else:
        return None


def navigation_data(user_id):
    response_section = group_sections(user_id)
    nav_bar = dict()
    if response_section:
        for data in response_section:
            temp = list(data.values())
            response_sub_section = get_sub_sections(user_id, temp[0])
            nav_bar.update({temp[0]: response_sub_section})
    return nav_bar

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
        
        try:
            page_allocation = PageAllocation.objects.get(id=page_id)
        except PageAllocation.DoesNotExist:
            # Handle the case when the PageAllocation with the given page_id does not exist
            return
        
        user = get_object_or_404(CustomUserTypes, id=user.id)
        privilege = Privilege.objects.create(pageallocation=page_allocation, is_active=True, assigned_users=user)

        privilege.save()


def update_priviledge(id, status):
    status = False if ('False' in status or 'false' in status) else True
    # Assuming you have the 'id' and 'status' variables available.
    # Convert 'status' to a boolean based on 'False' or 'false' in the input.   
    try:
        item = Privilege.objects.get(pk=id)
    except Privilege.DoesNotExist:
        # Handle the case when the Privilege with the given id does not exist
        return
    
    item.is_active = status
    item.save()

def get_page_priv(request):
    user = request.POST.get('user')
    if request.POST.get('id'):
        id = request.POST.get('id')
        sign = request.POST.get('sign')
        update_priviledge(id, sign)
    pages = process_load_privledge(user)
    return render(request,'base/loadprivPages.html', {'user':user, 'pages':pages})
