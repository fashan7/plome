import facebook

def fetch_leads():
    # Replace 'YOUR_ACCESS_TOKEN' with your actual Facebook access token
    access_token = 'EAAKFt0cZC5JMBOyEicP20LyES4jk7iQV1Q4l6ZCpQKv2PRbNV7o5VuPMEhZBP3gmUVhPsQHmi306n2BQ6AZBz9gJ9Y0GZBlKtZB39nayDgPjwRHkmGDZBfpj978vONwmXDodHq8f0Amxlc9GUnUxx0YE3OAUaNH9RehEEv8BxfHRYxTChmxTThv62CaBJViMFZBQhRSM0vQXbsivN6UZD'

    # Create an instance of the Facebook object with your API keys
    try:
        graph = facebook.GraphAPI(access_token=access_token, version="3.0")
    except facebook.GraphAPIError as e:
        print(f"Error connecting to Facebook Graph API: {e}")
        return

    leadgen_form_id = '1316143499002088'
    leads = []
    cursor = None

    while True:
        try:
            params = {'fields': 'field_data,ad_id', 'limit': 100}  # Adjust the limit as needed
            if cursor:
                params['after'] = cursor
            response = graph.get_object(f"/{leadgen_form_id}/leads", **params)
            leads.extend(response['data'])
            if 'paging' in response and 'cursors' in response['paging']:
                cursor = response['paging']['cursors']['after']
            else:
                break
        except facebook.GraphAPIError as e:
            print(f"Error retrieving leads: {e}")
            return

    leads_data = []
    for lead in leads:
       
        name = None
        email = None
        phone = None
        nom_de_la_campagne = None
        avez_vous_travaille = None
        status = None

        for field in lead['field_data']:
            if field['name'] == 'full_name':
                name = field['values'][0]
            elif field['name'] == 'email':
                email = field['values'][0]
            elif field['name'] == 'phone_number':
                phone = field['values'][0]
            elif field['name'] == 'nom_de_la_campagne':
                nom_de_la_campagne = field['values'][0]
            elif field['name'] == 'avez_vous_travaille':
                avez_vous_travaille = field['values'][0]

        if 'ad_id' in lead:
            status = 'new'
        else:
            status = 'expired'

        lead_data = {
            'Name': name,
            'Email': email,
            'Phone': phone,
            'Nom_de_la_campagne': nom_de_la_campagne,
            'Avez-vous_travaillé': avez_vous_travaille,
            'Status': status
        }
        leads_data.append(lead_data)

    return leads_data

if __name__ == "__main__":
    leads = fetch_leads()
    for lead in leads:
        print(lead)
